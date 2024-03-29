import contextlib
import json

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all
from ajna.utils.views import BaseChainView

GRANTS_SQL = """
    SELECT
          gp.proposal_id
        , gp.distribution_id
        , gp.proposer
        , gp.description
        , gp.total_tokens_requested
        , gp.params
        , gp.executed
        , gp.screening_votes_received
        , gp.funding_votes_received
        , gp.funding_votes_positive
        , gp.funding_votes_negative
        , gdp.start_block
        , gdp.end_block
        , gp.funding_start_block_number
        , gp.finalize_start_block_number
    FROM {grand_proposal_table} gp
    JOIN {grant_distribution_period_table} gdp
        ON gp.distribution_id = gdp.distribution_id
    ORDER BY gp.screening_votes_received DESC NULLS LAST
    LIMIT 10
"""


# Cache for 3 minutes so that we don't need to call the chain on every single request
@method_decorator(cache_page(60 * 3), name="dispatch")
class GrantsView(BaseChainView):
    def _funding_proposals(self, current_block):
        sql = """
            SELECT *
            FROM ({}) g
            WHERE g.funding_start_block_number <= %s
                AND g.finalize_start_block_number > %s
                AND g.end_block > %s
            ORDER BY g.funding_votes_received DESC NULLS LAST
        """.format(
            GRANTS_SQL.format(
                grand_proposal_table=self.models.grant_proposal._meta.db_table,
                grant_distribution_period_table=self.models.grant_distribution_period._meta.db_table,
            )
        )
        sql_vars = [current_block] * 3
        return sql, sql_vars

    def _finalize_proposals(self, current_block):
        sql = """
            SELECT *
            FROM ({}) g
            WHERE g.finalize_start_block_number <= %s
               AND g.end_block > %s
            ORDER BY g.funding_votes_positive DESC NULLS LAST
        """.format(
            GRANTS_SQL.format(
                grand_proposal_table=self.models.grant_proposal._meta.db_table,
                grant_distribution_period_table=self.models.grant_distribution_period._meta.db_table,
            )
        )
        sql_vars = [current_block] * 2
        return sql, sql_vars

    def get(self, request):
        current_block = self.chain.get_latest_block()
        if request.GET.get("type") == "finalize":
            sql, sql_vars = self._finalize_proposals(current_block)
        else:
            sql, sql_vars = self._funding_proposals(current_block)

        data = fetch_all(sql, sql_vars)

        for row in data:
            if row["description"]:
                with contextlib.suppress(json.decoder.JSONDecodeError):
                    row["description"] = json.loads(row["description"])
            if row["params"]:
                row["params"] = json.loads(row["params"])

        return Response(data, status.HTTP_200_OK)

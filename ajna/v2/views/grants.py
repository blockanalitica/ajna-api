import contextlib
import json

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from ajna.utils.views import RawSQLPaginatedChainView

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
    FROM {grand_proposal_table} gp
    JOIN {grant_distribution_period_table} gdp
        ON gp.distribution_id = gdp.distribution_id
"""


# Cache for 3 minutes so that we don't need to call the chain on every single request
@method_decorator(cache_page(60 * 3), name="dispatch")
class GrantsView(RawSQLPaginatedChainView):

    def _funding_proposals(self):
        current_block = self.chain.get_latest_block()
        sql = """
            {}
            WHERE gp.funding_start_block_number <= %s
                AND gp.finalize_start_block_number > %s
                AND gdp.end_block > %s
            ORDER BY gp.screening_votes_received DESC
        """.format(
            GRANTS_SQL.format(
                grand_proposal_table=self.models.grant_proposal._meta.db_table,
                grant_distribution_period_table=self.models.grant_distribution_period._meta.db_table,
            )
        )
        sql_vars = [current_block] * 3
        return sql, sql_vars

    def _finalize_proposals(self):
        current_block = self.chain.get_latest_block()
        sql = """
            {}
            WHERE gp.finalize_start_block_number <= %s
                AND gdp.end_block > %s
            ORDER BY gp.funding_votes_received DESC
        """.format(
            GRANTS_SQL.format(
                grand_proposal_table=self.models.grant_proposal._meta.db_table,
                grant_distribution_period_table=self.models.grant_distribution_period._meta.db_table,
            )
        )
        sql_vars = [current_block] * 2
        return sql, sql_vars

    def get_raw_sql(self, query_params, **kwargs):
        if query_params.get("type") == "finalize":
            sql, sql_vars = self._finalize_proposals()
        else:
            sql, sql_vars = self._funding_proposals()

        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            if row["description"]:
                with contextlib.suppress(json.decoder.JSONDecodeError):
                    row["description"] = json.loads(row["description"])
            if row["params"]:
                row["params"] = json.loads(row["params"])
        return data

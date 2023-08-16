from django.db import connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response

from ajna.utils.db import fetch_all

from . import BaseChainView


# Cache for 3 minutes so that we don't need to call the chain on every single request
@method_decorator(cache_page(60 * 3), name="dispatch")
class FundingProposalsView(BaseChainView):
    def get(self, request):
        current_block = self.chain.get_latest_block()
        sql_vars = [current_block, current_block, current_block]
        sql = """
            SELECT
                  p.description
                , p.description->>'title' AS title
                , p.total_tokens_requested
                , p.screening_votes_received
            FROM {grant_proposal_table} AS p
            WHERE p.funding_start_block_number <= %s
                AND p.finalize_start_block_number > %s
                AND p.end_block > %s
            ORDER BY p.screening_votes_received DESC
            LIMIT 10
        """.format(
            grant_proposal_table=self.models.grant_proposal._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            proposals = fetch_all(cursor)

        return Response(proposals, status.HTTP_200_OK)


# Cache for 3 minutes so that we don't need to call the chain on every single request
@method_decorator(cache_page(60 * 3), name="dispatch")
class FinalizeProposalsView(BaseChainView):
    def get(self, request):
        current_block = self.chain.get_latest_block()
        sql_vars = [current_block, current_block]
        sql = """
            SELECT
                  p.description
                , p.description->>'title' AS title
                , p.total_tokens_requested
                , p.screening_votes_received
                , p.funding_votes_received
            FROM {grant_proposal_table} AS p
            WHERE p.finalize_start_block_number <= %s
                AND p.end_block > %s
            ORDER BY p.funding_votes_received DESC
            LIMIT 10
        """.format(
            grant_proposal_table=self.models.grant_proposal._meta.db_table,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, sql_vars)
            proposals = fetch_all(cursor)

        return Response(proposals, status.HTTP_200_OK)

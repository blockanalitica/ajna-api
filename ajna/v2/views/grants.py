import contextlib
import json

from ajna.utils.views import RawSQLPaginatedChainView


class GrantsView(RawSQLPaginatedChainView):
    default_order = "-proposal_id"

    def get_raw_sql(self, **kwargs):
        sql = """
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

        """.format(
            grand_proposal_table=self.models.grant_proposal._meta.db_table,
            grant_distribution_period_table=self.models.grant_distribution_period._meta.db_table,
        )
        sql_vars = []
        return sql, sql_vars

    def serialize_data(self, data):
        for row in data:
            if row["description"]:
                with contextlib.suppress(json.decoder.JSONDecodeError):
                    row["description"] = json.loads(row["description"])
            if row["params"]:
                row["params"] = json.loads(row["params"])
        return data

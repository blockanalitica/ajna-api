import logging

from discord_webhook import DiscordEmbed, DiscordWebhook
from django.conf import settings

from ajna.utils.db import fetch_one

log = logging.getLogger(__name__)


def _format_decimal(value, currency):
    decimal_places = 5 if abs(value) < 1.1 else 2
    return f"{round(value, decimal_places)!s} {currency}"


def _format_auction_uid(auction_uid):
    return f"{auction_uid[:4]}...{auction_uid[-4:]}"


def _send_embed_to_ajna_discord(embed):
    if not settings.DISCORD_WEBHOOK_AJNA_NOTIFICATIONS:
        return

    if not embed:
        log.debug("Missing embed")
        return

    webhook = DiscordWebhook(
        url=settings.DISCORD_WEBHOOK_AJNA_NOTIFICATIONS,
        rate_limit_retry=True,
    )
    webhook.add_embed(embed)
    request = webhook.execute()
    request.raise_for_status()


def _send_kick_notification(chain, event):
    sql = f"""
        SELECT
              ak.auction_uid
            , ak.collateral
            , ak.debt
            , ak.bond
            , p.collateral_token_symbol
            , p.quote_token_symbol
        FROM {chain.auction_kick._meta.db_table} ak
        JOIN {chain.pool._meta.db_table} p
            ON ak.pool_address = p.address
        WHERE ak.order_index = %s
    """

    data = fetch_one(sql, [event.order_index])

    description = "Auction {} was kicked in {} / {} pool".format(
        _format_auction_uid(data["auction_uid"]),
        data["collateral_token_symbol"],
        data["quote_token_symbol"],
    )
    url = "https://info.ajna.finance/{}/auctions/{}".format(chain.chain, data["auction_uid"])
    embed = DiscordEmbed(
        title="Auction Kicked",
        description=description,
        url=url,
        color="ff3344",
    )
    embed.set_footer(text=f"Network: {chain.chain.capitalize()}")
    embed.set_timestamp()
    embed.add_embed_field(
        name="Collateral",
        value=_format_decimal(data["collateral"], data["collateral_token_symbol"]),
    )
    embed.add_embed_field(
        name="Debt", value=_format_decimal(data["debt"], data["quote_token_symbol"])
    )
    embed.add_embed_field(
        name="Bond", value=_format_decimal(data["bond"], data["quote_token_symbol"])
    )

    _send_embed_to_ajna_discord(embed)


def _send_auction_settle_notification(chain, event):
    sql = f"""
        SELECT
              aus.auction_uid
            , a.collateral
            , a.debt
            , p.collateral_token_symbol
            , p.quote_token_symbol
        FROM {chain.auction_auction_settle._meta.db_table} aus
        JOIN {chain.pool._meta.db_table} p
            ON aus.pool_address = p.address
        JOIN {chain.auction._meta.db_table} a
            ON aus.auction_uid = a.uid
        WHERE aus.order_index = %s
    """

    data = fetch_one(sql, [event.order_index])
    description = "Auction {} was settled in {} / {} pool".format(
        _format_auction_uid(data["auction_uid"]),
        data["collateral_token_symbol"],
        data["quote_token_symbol"],
    )
    url = "https://info.ajna.finance/{}/auctions/{}".format(chain.chain, data["auction_uid"])
    embed = DiscordEmbed(
        title="Auction Settled",
        description=description,
        url=url,
        color="2a9340",
    )
    embed.set_footer(text=f"Network: {chain.chain.capitalize()}")
    embed.set_timestamp()
    embed.add_embed_field(
        name="Collateral",
        value=_format_decimal(data["collateral"], data["collateral_token_symbol"]),
    )
    embed.add_embed_field(
        name="Debt", value=_format_decimal(data["debt"], data["quote_token_symbol"])
    )

    _send_embed_to_ajna_discord(embed)


def send_notification_for_event(chain, event):
    try:
        match event.name:
            case "Kick":
                _send_kick_notification(chain, event)
            case "AuctionSettle":
                _send_auction_settle_notification(chain, event)

    except Exception:
        log.exception("Can't send auction notification to discord")

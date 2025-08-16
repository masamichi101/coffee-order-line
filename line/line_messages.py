from django.conf import settings
from django.utils import timezone

from linebot import LineBotApi
from linebot.models import (
    FlexSendMessage,
)

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)


# 注文確定
def send_order_confirm_message(line_id, order):
    content_json = {
        "type": "flex",
        "altText": "注文完了しました",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "flex": 0,
                "contents": [
                    {
                        "type": "text",
                        "text": "注文完了",
                        "weight": "bold",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "注文番号",
                                    },
                                    {
                                        "type": "text",
                                        "text": str(order.id),
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "注文日時",
                                    },
                                    {
                                        "type": "text",
                                        "text": timezone.localtime(order.created_at).strftime("%Y年%m月%d日 %H:%M"),
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "ショップ",
                                    },
                                    {
                                        "type": "text",
                                        "text": order.shop.name,
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "住所",
                                    },
                                    {
                                        "type": "text",
                                        "text": order.shop.address or "未設定",
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "電話番号",
                                    },
                                    {
                                        "type": "text",
                                        "text": order.shop.tel or "未設定",
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "受け取り予定",
                                    },
                                    {
                                        "type": "text",
                                        "text": timezone.localtime(order.pickup_time).strftime("%H:%M") if order.pickup_time else "未設定",
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "合計金額",
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{order.total_amount}円",
                                        "align": "end",
                                    },
                                ],
                            },
                        ],
                    }
                ],
            },
        },
    }

    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)


# 注文がある場合
def send_menu_message(line_id):
    content_json = {
        "type": "flex",
        "altText": "メニューを選択してください",
        "contents": {
            "type": "bubble",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "メニューを選択してください",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "注文確認",
                            "text": "注文確認",
                        },
                        "style": "primary",
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "注文変更",
                            "text": "注文変更",
                        },
                        "style": "primary",
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "注文キャンセル",
                            "text": "注文キャンセル",
                        },
                        "style": "secondary",
                    },
                ],
            },
        },
    }

    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)


# 注文がない場合
def send_new_menu_message(line_id):
    content_json = {
        "type": "flex",
        "altText": "メニューを選択してください",
        "contents": {
            "type": "bubble",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "新規注文",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "注文メニュー",
                            "uri": f"https://liff.line.me/{settings.LIFF_ID}",
                        },
                        "style": "primary",
                    }
                ],
            },
        },
    }

    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)


# 注文確認
def send_check_order_message(line_id, orders):
    content_json = {
        "type": "flex",
        "altText": "注文確認",
        "contents": {
            "type": "bubble",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "確認したい注文を選択してください",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [],
            },
        },
    }

    buttons = []
    for order in orders:
        local_date = timezone.localtime(order.created_at)
        button = {
            "type": "button",
            "action": {
                "type": "postback",
                "label": f"注文#{order.id} - {local_date.strftime('%m/%d %H:%M')}",
                "text": f"注文#{order.id} - {local_date.strftime('%m/%d %H:%M')}",
                "data": f"action=注文確認&order_id={order.id}",
            },
            "style": "primary",
        }
        buttons.append(button)

    content_json["contents"]["body"]["contents"] = buttons
    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)


# 注文確認詳細
def send_check_order_detail_message(line_id, order):
    local_date = timezone.localtime(order.created_at)

    content_json = {
        "type": "flex",
        "altText": "注文確認",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "flex": 0,
                "contents": [
                    {
                        "type": "text",
                        "text": "注文確認",
                        "weight": "bold",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "注文番号",
                                    },
                                    {
                                        "type": "text",
                                        "text": str(order.id),
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "注文日時",
                                    },
                                    {
                                        "type": "text",
                                        "text": local_date.strftime("%Y年%m月%d日 %H:%M"),
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "ショップ",
                                    },
                                    {
                                        "type": "text",
                                        "text": order.shop.name,
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "ステータス",
                                    },
                                    {
                                        "type": "text",
                                        "text": order.get_status_display(),
                                        "align": "end",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "合計金額",
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{order.total_amount}円",
                                        "align": "end",
                                    },
                                ],
                            },
                        ],
                    }
                ],
            },
        },
    }

    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)


# 注文変更
def send_change_order_message(line_id, orders):
    content_json = {
        "type": "flex",
        "altText": "注文変更",
        "contents": {
            "type": "bubble",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "変更したい注文を選択してください",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [],
            },
        },
    }

    buttons = []
    for order in orders:
        local_date = timezone.localtime(order.created_at)

        button = {
            "type": "button",
            "action": {
                "type": "uri",
                "label": f"注文#{order.id} - {local_date.strftime('%m/%d %H:%M')}",
                "uri": f"https://liff.line.me/{settings.LIFF_ID}?order_id={order.id}",
            },
            "style": "primary",
        }
        buttons.append(button)

    content_json["contents"]["body"]["contents"] = buttons
    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)


# 注文キャンセル
def send_cancel_order_message(line_id, orders):
    content_json = {
        "type": "flex",
        "altText": "注文キャンセル",
        "contents": {
            "type": "bubble",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "キャンセルしたい注文を選択してください",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [],
            },
        },
    }

    buttons = []
    for order in orders:
        local_date = timezone.localtime(order.created_at)

        button = {
            "type": "button",
            "action": {
                "type": "postback",
                "label": f"注文#{order.id} - {local_date.strftime('%m/%d %H:%M')}",
                "text": f"注文#{order.id} - {local_date.strftime('%m/%d %H:%M')}",
                "data": f"action=注文キャンセル&order_id={order.id}",
            },
            "style": "secondary",
        }
        buttons.append(button)

    content_json["contents"]["body"]["contents"] = buttons
    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)

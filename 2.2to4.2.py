import pandas as pd
import json
import datetime
import os
import argparse
import requests  # 引入 requests 库

# UIGF v2.2 祈愿类型与 gacha_type/uigf_gacha_type 的映射
UIGF_V2_2_GACHA_TYPE_MAPPING = {
    "新手祈愿": {"uigf_gacha_type": "100", "gacha_type": "100"},
    "常驻祈愿": {"uigf_gacha_type": "200", "gacha_type": "200"},
    "角色活动祈愿": {
        "uigf_gacha_type": "301",
        "gacha_type": "301",
    },  # v2.2 兼容 301|400
    "角色活动祈愿-2": {
        "uigf_gacha_type": "301",
        "gacha_type": "400",
    },  # 角色活动祈愿-2 对应 gacha_type 400
    "武器活动祈愿": {"uigf_gacha_type": "302", "gacha_type": "302"},
}

# 列名映射字典
COLUMN_MAPS = {
    "原始数据": {  # 适用于包含 '原始数据' 表的情况
        "time": "time",
        "name": "name",
        "item_type": "item_type",
        "rank_type": "rank_type",
        "id": "id",
        "uigf_gacha_type": "uigf_gacha_type",
        "gacha_type": "gacha_type",
        "item_id": "item_id",  # 原始数据表可能包含 item_id
        "count": "count",
    },
    "祈愿表": {  # 适用于 '角色活动祈愿', '武器活动祈愿' 等分析表
        "时间": "time",
        "名称": "name",
        "类别": "item_type",
        "星级": "rank_type",
        "祈愿 Id": "id",
        # '总次数', '保底内' 这些分析列在此处不直接映射到 v4.2 list item 字段
    },
}

# 物品名称到 item_id 的映射字典 (全局缓存)
ITEM_ID_MAP = None
ITEM_ID_API_URL = "https://api.uigf.org/dict/genshin/chs.json"


def _get_item_id_map():
    """
    从 UIGF 官方 API 获取物品名称到 item_id 的映射字典，并缓存。
    """
    global ITEM_ID_MAP
    if ITEM_ID_MAP is not None:
        return ITEM_ID_MAP

    print(f"正在从 {ITEM_ID_API_URL} 获取 item_id 映射字典...")
    try:
        response = requests.get(ITEM_ID_API_URL, timeout=10)  # 设置超时
        response.raise_for_status()  # 检查 HTTP 错误状态
        ITEM_ID_MAP = response.json()
        print("成功获取 item_id 映射字典。")
        return ITEM_ID_MAP
    except requests.exceptions.RequestException as e:
        print(f"警告: 无法从 {ITEM_ID_API_URL} 获取 item_id 映射字典。原因: {e}")
        print("部分记录的 item_id 可能会被设置为空字符串。")
        return None
    except json.JSONDecodeError as e:
        print(f"警告: 无法解析 {ITEM_ID_API_URL} 返回的 JSON 数据。原因: {e}")
        print("部分记录的 item_id 可能会被设置为空字符串。")
        return None


def convert_uigf_excel_to_4_2_json(
    excel_path: str,
    output_path: str,
    provided_uid: str,
    provided_lang: str = None,
    provided_timezone: int = 8,
):
    """
    将UIGF v2.2 Excel文件 (原神祈愿记录) 转换为UIGF v4.2 JSON格式。
    支持读取 '原始数据' 或各类 '祈愿表'，并尝试从 UIGF API 补充 item_id。

    Args:
        excel_path (str): UIGF v2.2 Excel文件的路径。
        output_path (str): 转换后的UIGF v4.2 JSON文件的保存路径。
        provided_uid (str): 用户的UID，此为必需参数。
        provided_lang (str, optional): 语言代码 (如 'zh-cn')，默认为 'zh-cn'。
        provided_timezone (int, optional): 时区偏移量，默认为 8 (UTC+8)。
    """
    # 尝试获取 item_id 映射字典
    item_id_map = _get_item_id_map()

    print(f"正在读取Excel文件: {excel_path}...")
    try:
        xls = pd.ExcelFile(excel_path, engine="openpyxl")
        all_sheet_names = xls.sheet_names
        print(f"找到的工作表: {all_sheet_names}")
    except FileNotFoundError:
        print(f"错误: 未找到文件 '{excel_path}'。请检查路径是否正确。")
        return
    except Exception as e:
        print(f"读取Excel文件时发生错误: {e}")
        return

    uid = str(provided_uid)
    if not uid.isdigit() or len(uid) not in [9, 10]:  # 简单的UID格式校验
        print(f"错误: 提供的UID '{uid}' 格式不正确。请提供一个有效的9-10位数字UID。")
        return
    print(f"使用的UID: {uid}")

    # --- 提取和校验语言 (lang) ---
    valid_langs = [
        "de-de",
        "en-us",
        "es-es",
        "fr-fr",
        "id-id",
        "it-it",
        "ja-jp",
        "ko-kr",
        "pt-pt",
        "ru-ru",
        "th-th",
        "tr-tr",
        "vi-vn",
        "zh-cn",
        "zh-tw",
    ]
    lang = (
        provided_lang.lower().replace("_", "-") if provided_lang else "zh-cn"
    )  # 优先使用提供的语言，并处理 zh_cn -> zh-cn

    # 尝试从Excel的“原始数据”表或第一个“祈愿表”中提取语言，但命令行提供的优先
    if "原始数据" in all_sheet_names and not provided_lang:
        try:
            temp_df = xls.parse("原始数据")
            if "lang" in temp_df.columns:
                non_empty_langs = temp_df["lang"].dropna().astype(str).unique()
                if len(non_empty_langs) > 0:
                    extracted_lang = str(non_empty_langs[0]).lower().replace("_", "-")
                    if extracted_lang in valid_langs:
                        lang = extracted_lang
                        print(f"从'原始数据'工作表提取语言: {lang}")
                    else:
                        print(
                            f"警告: '原始数据'中提取的语言 '{extracted_lang}' 不在UIGF v4.2的合法语言列表中。将使用默认语言 '{lang}'。"
                        )
        except Exception as e:
            print(f"警告: 尝试从'原始数据'工作表提取语言失败: {e}")

    if lang not in valid_langs:  # 最终确认语言是否合法
        lang = "zh-cn"  # 如果提供的或提取的语言最终仍不合法，回退到中文
    print(f"使用的语言: {lang}")
    print(f"使用的时区偏移: {provided_timezone}")

    # --- 准备UIGF v4.2 JSON的基本结构 ---
    now = datetime.datetime.now()
    export_timestamp = int(now.timestamp())  # 秒级时间戳

    uigf_v4_json = {
        "info": {
            "export_timestamp": export_timestamp,
            "export_app": "UIGF_v2.2_Excel_to_v4.2_JSON_Converter",
            "export_app_version": "1.2",  # 更新版本号
            "version": "v4.2",
        },
        "hk4e": [  # 原神数据存储在 'hk4e' 字段下
            {"uid": uid, "timezone": provided_timezone, "lang": lang, "list": []}
        ],
    }

    all_gacha_records = []

    # UIGF v4.2 'hk4e.list' 中必需的字段 (即使Excel中可能缺失，也需确保处理)
    # item_id 和 count 即使在 v2.2 祈愿表中缺失，也应在 v4.2 中提供
    required_for_v4_2_item_core = ["id", "time", "uigf_gacha_type", "gacha_type"]

    # UIGF v4.2 'hk4e.list' 中 'gacha_type' 和 'uigf_gacha_type' 的合法枚举值
    valid_uigf_gacha_types = ["100", "200", "301", "302", "500"]
    valid_gacha_types = ["100", "200", "301", "302", "400", "500"]

    processed_sheets_count = 0

    # --- 优先处理 '原始数据' 表 ---
    if "原始数据" in all_sheet_names:
        print("\n--- 正在处理 '原始数据' 工作表 ---")
        try:
            df = xls.parse("原始数据")
            current_sheet_name = "原始数据"
            processed_sheets_count += 1

            for index, row in df.iterrows():
                record = {}
                row_num = index + 2  # Excel中的实际行号 (1-indexed表头 + 1数据行偏移)

                # 使用 '原始数据' 的列名映射
                mapped_row = {
                    v: row[k]
                    for k, v in COLUMN_MAPS["原始数据"].items()
                    if k in row and pd.notna(row[k])
                }

                # 校验核心字段
                is_row_valid = True
                for col in required_for_v4_2_item_core:
                    if (
                        col not in mapped_row
                        or mapped_row[col] is None
                        or str(mapped_row[col]).strip() == ""
                    ):
                        print(
                            f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行缺少必需的字段 '{col}' 或其值为空。该行将被跳过。"
                        )
                        is_row_valid = False
                        break
                if not is_row_valid:
                    continue

                record["uigf_gacha_type"] = str(mapped_row.get("uigf_gacha_type", ""))
                record["gacha_type"] = str(mapped_row.get("gacha_type", ""))
                record["id"] = str(mapped_row.get("id", ""))

                # item_id 优先从 Excel 获取
                record["item_id"] = str(mapped_row.get("item_id", ""))
                # 如果 Excel 中没有 item_id，尝试从 API 字典获取
                if not record["item_id"] and item_id_map and mapped_row.get("name"):
                    looked_up_id = item_id_map.get(mapped_row["name"])
                    if looked_up_id is not None:
                        record["item_id"] = str(looked_up_id)
                    else:
                        print(
                            f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行，物品名称 '{mapped_row['name']}' 在 UIGF 字典中未找到对应的 item_id。item_id 将设置为空字符串。"
                        )
                elif not record["item_id"] and not item_id_map:
                    print(
                        f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行，无法获取 item_id 映射字典。item_id 将设置为空字符串。"
                    )
                elif not record["item_id"] and not mapped_row.get("name"):
                    print(
                        f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行，物品名称为空，无法查找 item_id。item_id 将设置为空字符串。"
                    )

                record["count"] = str(mapped_row.get("count", "1"))  # 默认值为 '1'

                try:
                    record["time"] = pd.to_datetime(mapped_row.get("time")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                except Exception:
                    print(
                        f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行的 'time' 字段 '{mapped_row.get('time')}' 格式无效。该行将被跳过。"
                    )
                    continue

                record["name"] = str(mapped_row.get("name", ""))
                record["item_type"] = str(mapped_row.get("item_type", ""))
                record["rank_type"] = str(mapped_row.get("rank_type", ""))

                # 进一步校验字段值
                if not record["id"].isdigit() or not (1 <= len(record["id"]) <= 19):
                    print(
                        f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行的 'id' 字段 '{record['id']}' 不符合UIGF v4.2规范（1-19位数字字符串）。该记录将被跳过。"
                    )
                    continue
                if record["uigf_gacha_type"] not in valid_uigf_gacha_types:
                    print(
                        f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行的 uigf_gacha_type '{record['uigf_gacha_type']}' 不在 v4.2 的合法列表中。该记录将被跳过。"
                    )
                    continue
                if record["gacha_type"] not in valid_gacha_types:
                    print(
                        f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行的 gacha_type '{record['gacha_type']}' 不在 v4.2 的合法列表中。该记录将被跳过。"
                    )
                    continue
                if record["item_id"] == "":  # 最终校验 item_id 是否为空
                    print(
                        f"警告: 在 '{current_sheet_name}' 表的第 {row_num} 行，item_id 最终仍为空。请注意这可能导致部分工具无法识别该记录。"
                    )

                all_gacha_records.append(record)
            print(f"已从 '原始数据' 表处理 {len(df)} 条记录。")
        except Exception as e:
            print(f"处理 '原始数据' 工作表时发生错误: {e}")

    # --- 遍历其他可能的祈愿表 ---
    for sheet_name in all_sheet_names:
        if sheet_name == "原始数据":  # 已经处理过，跳过
            continue

        if sheet_name in UIGF_V2_2_GACHA_TYPE_MAPPING:
            print(f"\n--- 正在处理 '{sheet_name}' 工作表 ---")
            processed_sheets_count += 1
            try:
                df = xls.parse(sheet_name)
                gacha_type_info = UIGF_V2_2_GACHA_TYPE_MAPPING[sheet_name]
                sheet_uigf_gacha_type = gacha_type_info["uigf_gacha_type"]
                sheet_gacha_type = gacha_type_info["gacha_type"]

                for index, row in df.iterrows():
                    record = {}
                    row_num = index + 2  # Excel中的实际行号

                    # 使用 '祈愿表' 的列名映射
                    mapped_row = {
                        v: row[k]
                        for k, v in COLUMN_MAPS["祈愿表"].items()
                        if k in row and pd.notna(row[k])
                    }

                    # 为祈愿表添加推断的 gacha_type 和 uigf_gacha_type
                    record["uigf_gacha_type"] = sheet_uigf_gacha_type
                    record["gacha_type"] = sheet_gacha_type
                    record["count"] = "1"  # 祈愿表通常每行是一次抽取，count为1

                    # item_id: 从 API 获取，如果获取失败或名称未找到，则设为空字符串
                    record["item_id"] = ""  # 祈愿表通常没有 item_id, 先设为空字符串
                    if item_id_map and mapped_row.get("name"):
                        looked_up_id = item_id_map.get(mapped_row["name"])
                        if looked_up_id is not None:
                            record["item_id"] = str(looked_up_id)
                        else:
                            print(
                                f"警告: 在 '{sheet_name}' 表的第 {row_num} 行，物品名称 '{mapped_row['name']}' 在 UIGF 字典中未找到对应的 item_id。item_id 将设置为空字符串。"
                            )
                    elif not item_id_map:
                        print(
                            f"警告: 在 '{sheet_name}' 表的第 {row_num} 行，无法获取 item_id 映射字典。item_id 将设置为空字符串。"
                        )
                    elif not mapped_row.get("name"):
                        print(
                            f"警告: 在 '{sheet_name}' 表的第 {row_num} 行，物品名称为空，无法查找 item_id。item_id 将设置为空字符串。"
                        )

                    # 校验核心字段 (id, time)
                    is_row_valid = True
                    for col_key, mapped_key in [("祈愿 Id", "id"), ("时间", "time")]:
                        if (
                            mapped_key not in mapped_row
                            or mapped_row[mapped_key] is None
                            or str(mapped_row[mapped_key]).strip() == ""
                        ):
                            print(
                                f"警告: 在 '{sheet_name}' 表的第 {row_num} 行缺少必需的字段 '{col_key}' 或其值为空。该行将被跳过。"
                            )
                            is_row_valid = False
                            break
                    if not is_row_valid:
                        continue

                    record["id"] = str(mapped_row.get("id", ""))
                    try:
                        record["time"] = pd.to_datetime(
                            mapped_row.get("time")
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        print(
                            f"警告: 在 '{sheet_name}' 表的第 {row_num} 行的 'time' 字段 '{mapped_row.get('time')}' 格式无效。该行将被跳过。"
                        )
                        continue

                    record["name"] = str(mapped_row.get("name", ""))
                    record["item_type"] = str(mapped_row.get("item_type", ""))
                    record["rank_type"] = str(mapped_row.get("rank_type", ""))

                    # 进一步校验字段值
                    if not record["id"].isdigit() or not (1 <= len(record["id"]) <= 19):
                        print(
                            f"警告: 在 '{sheet_name}' 表的第 {row_num} 行的 'id' 字段 '{record['id']}' 不符合UIGF v4.2规范（1-19位数字字符串）。该记录将被跳过。"
                        )
                        continue
                    if record["uigf_gacha_type"] not in valid_uigf_gacha_types:
                        print(
                            f"警告: 在 '{sheet_name}' 表的第 {row_num} 行推断的 uigf_gacha_type '{record['uigf_gacha_type']}' 不在 v4.2 的合法列表中。该记录将被跳过。"
                        )
                        continue
                    if record["gacha_type"] not in valid_gacha_types:
                        print(
                            f"警告: 在 '{sheet_name}' 表的第 {row_num} 行推断的 gacha_type '{record['gacha_type']}' 不在 v4.2 的合法列表中。该记录将被跳过。"
                        )
                        continue
                    if record["item_id"] == "":  # 最终校验 item_id 是否为空
                        print(
                            f"警告: 在 '{sheet_name}' 表的第 {row_num} 行，item_id 最终仍为空。请注意这可能导致部分工具无法识别该记录。"
                        )

                    all_gacha_records.append(record)
                print(f"已从 '{sheet_name}' 表处理 {len(df)} 条记录。")
            except Exception as e:
                print(f"处理 '{sheet_name}' 工作表时发生错误: {e}")
        else:
            print(f"信息: 忽略未知工作表 '{sheet_name}'。")

    if processed_sheets_count == 0:
        print(
            "错误: 未能在Excel文件中找到任何可处理的祈愿数据工作表（'原始数据' 或标准祈愿类型表）。"
        )
        return

    # 对所有合并的记录进行排序 (按 'id' 升序，与 v4.2 示例一致)
    all_gacha_records.sort(key=lambda x: int(x["id"]))
    uigf_v4_json["hk4e"][0]["list"] = all_gacha_records
    print(f"\n总计处理 {len(all_gacha_records)} 条有效祈愿记录。")

    # --- 保存为JSON文件 ---
    print(f"正在保存JSON文件至: {output_path}...")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(uigf_v4_json, f, ensure_ascii=False, indent=2)
        print(f"成功将Excel文件转换为UIGF v4.2 JSON格式，并保存至: {output_path}")
    except Exception as e:
        print(f"保存JSON文件时发生错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="将UIGF v2.2 Excel抽卡记录 (原神) 转换为UIGF v4.2 JSON格式。"
    )
    parser.add_argument("input_excel", help="输入UIGF v2.2 Excel文件的路径。")
    parser.add_argument("output_json", help="输出UIGF v4.2 JSON文件的路径。")
    parser.add_argument(
        "--uid",
        type=str,
        required=True,  # UID现在是必需的
        help="强制指定UID。此参数为必需。",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default=None,
        help="强制指定语言代码（如 'zh-cn'）。如果未提供，会尝试从Excel中提取或默认为 'zh-cn'。",
    )
    parser.add_argument(
        "--timezone", type=int, default=8, help="时区偏移量，默认为 8 (UTC+8)。"
    )

    args = parser.parse_args()

    # 如果输出路径包含目录，则创建目录
    output_dir = os.path.dirname(args.output_json)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"已创建输出目录: {output_dir}")
        except OSError as e:
            print(f"错误: 无法创建输出目录 '{output_dir}': {e}")
            return

    convert_uigf_excel_to_4_2_json(
        args.input_excel,
        args.output_json,
        provided_uid=args.uid,
        provided_lang=args.lang,
        provided_timezone=args.timezone,
    )


if __name__ == "__main__":
    main()

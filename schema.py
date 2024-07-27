uigf3 = {
    "type": "object",
    "properties": {
        "info": {
            "type": "object",
            "properties": {
                "uid": {"type": "string", "title": "UID of the export record"},
                "lang": {
                    "type": "string",
                    "title": "language in the format of languagecode2-country/regioncode2",
                },
                "export_timestamp": {
                    "type": "number",
                    "title": "Export UNIX timestamp (accurate to the second)",
                },
                "export_time": {
                    "type": "string",
                    "title": "Export time",
                    "description": "yyyy-MM-dd HH:mm:ss",
                },
                "export_app": {
                    "type": "string",
                    "title": "Name of the export application",
                },
                "export_app_version": {
                    "type": "string",
                    "title": "Version of the export application",
                },
                "uigf_version": {
                    "type": "string",
                    "title": "UIGF version; follow the regular expression pattern",
                    "pattern": "v\\d+\\.\\d+",
                },
                "region_time_zone": {
                    "type": "number",
                    "title": "Region timezone offset",
                },
            },
            "required": ["uid", "uigf_version"],
            "title": "UIGF Export Information",
        },
        "list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "uigf_gacha_type": {
                        "type": "string",
                        "title": "UIGF gacha type",
                        "description": "Used to differentiate different gacha types with the same pity calculation for items",
                    },
                    "gacha_type": {"type": "string", "title": "Gacha type"},
                    "item_id": {"type": "string", "title": "Internal ID of the item"},
                    "count": {"type": "string", "title": "Count, usually 1"},
                    "time": {
                        "type": "string",
                        "title": "Time when the item was obtained. This MUST BE THE String typed value captured intact from the gacha record webpage WITHOUT ANY CONVERTION TO ANY DATE TYPES. Any conversion of such can cause potential timezone mistakes if the device time zone differs from the server time zone, unless special treatments are applied by individual app devs.",
                    },
                    "name": {"type": "string", "title": "Item name"},
                    "item_type": {"type": "string", "title": "Item type"},
                    "rank_type": {"type": "string", "title": "Item rank"},
                    "id": {"type": "string", "title": "Internal ID of the record"},
                },
                "required": ["uigf_gacha_type", "gacha_type", "id", "item_id", "time"],
                "title": "UIGF Item",
            },
            "title": "Item List",
        },
    },
    "required": ["info", "list"],
    "title": "UIGF Root Object",
}

uigf24 = {
    "type": "object",
    "properties": {
        "info": {
            "type": "object",
            "properties": {
                "uid": {"type": "string", "title": "导出记录的 UID"},
                "lang": {
                    "type": "string",
                    "title": "语言 languagecode2-country/regioncode2",
                },
                "export_timestamp": {
                    "type": "number",
                    "title": "导出 UNIX 时间戳（秒）",
                },
                "export_time": {
                    "type": "string",
                    "title": "导出时间",
                    "description": "yyyy-MM-dd HH:mm:ss",
                },
                "export_app": {"type": "string", "title": "导出 App 名称"},
                "export_app_version": {"type": "string", "title": "导出 App 版本"},
                "uigf_version": {
                    "type": "string",
                    "title": "UIGF 版本号",
                    "pattern": "v\\d+\\.\\d+",
                },
                "region_time_zone": {"type": "number", "title": "区域时区偏移"},
            },
            "required": ["uid", "uigf_version"],
            "title": "UIGF 导出信息",
        },
        "list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "uigf_gacha_type": {
                        "type": "string",
                        "title": "UIGF 卡池类型",
                        "description": "用于区分卡池类型不同，但卡池保底计算相同的物品",
                    },
                    "gacha_type": {"type": "string", "title": "卡池类型"},
                    "item_id": {"type": "string", "title": "物品的内部 ID"},
                    "count": {"type": "string", "title": "个数，一般为1"},
                    "time": {"type": "string", "title": "获取物品的时间"},
                    "name": {"type": "string", "title": "物品名称"},
                    "item_type": {"type": "string", "title": "物品类型"},
                    "rank_type": {"type": "string", "title": "物品等级"},
                    "id": {"type": "string", "title": "记录内部 ID"},
                },
                "required": ["uigf_gacha_type", "gacha_type", "id", "item_id", "time"],
                "title": "UIGF 物品",
            },
            "title": "物品列表",
        },
    },
    "required": ["info", "list"],
    "title": "UIGF 根对象",
}

uigf23 = {
    "root": {
        "type": "object",
        "properties": {
            "info": {
                "type": "object",
                "properties": {
                    "uid": {"type": "string", "title": "导出记录的 UID"},
                    "lang": {
                        "type": "string",
                        "title": "语言 languagecode2-country/regioncode2",
                    },
                    "export_timestamp": {
                        "type": "number",
                        "title": "导出 UNIX 时间戳（秒）",
                    },
                    "export_time": {
                        "type": "string",
                        "title": "导出时间",
                        "description": "yyyy-MM-dd HH:mm:ss",
                    },
                    "export_app": {"type": "string", "title": "导出 App 名称"},
                    "export_app_version": {"type": "string", "title": "导出 App 版本"},
                    "uigf_version": {
                        "type": "string",
                        "title": "UIGF 版本号",
                        "pattern": "v\\d+\\.\\d+",
                    },
                },
                "required": ["uid", "uigf_version"],
                "title": "UIGF 导出信息",
            },
            "list": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "uigf_gacha_type": {
                            "type": "string",
                            "title": "UIGF 卡池类型",
                            "description": "用于区分卡池类型不同，但卡池保底计算相同的物品",
                        },
                        "gacha_type": {"type": "string", "title": "卡池类型"},
                        "item_id": {"type": "string", "title": "物品的内部 ID"},
                        "count": {
                            "type": "string",
                            "title": "个数",
                            "description": "一般为1",
                        },
                        "time": {"type": "string", "title": "获取物品的时间"},
                        "name": {"type": "string", "title": "物品名称"},
                        "item_type": {"type": "string", "title": "物品类型"},
                        "rank_type": {"type": "string", "title": "物品等级"},
                        "id": {"type": "string", "title": "记录内部 ID"},
                    },
                    "required": [
                        "uigf_gacha_type",
                        "gacha_type",
                        "id",
                        "item_id",
                        "time",
                    ],
                    "title": "UIGF 物品",
                },
                "title": "物品列表",
            },
        },
        "required": ["info", "list"],
        "title": "UIGF 根对象",
    }
}

srgf = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "info": {
            "type": "object",
            "properties": {
                "uid": {"type": "string"},
                "lang": {
                    "type": "string",
                    "description": "语言 languagecode2-country/regioncode2",
                },
                "region_time_zone": {"type": "number", "description": "时区"},
                "export_timestamp": {
                    "type": "number",
                    "description": "导出 UNIX 时间戳",
                },
                "export_app": {"type": "string", "description": "导出的 App 名称"},
                "export_app_version": {
                    "type": "string",
                    "description": "导出此份记录的 App 版本号",
                },
                "srgf_version": {
                    "type": "string",
                    "description": "所应用的 SRGF 的版本,包含此字段以防 SRGF 出现中断性变更时，App 无法处理",
                },
            },
            "description": "包含导出方定义的基本信息",
            "required": ["srgf_version", "uid", "lang", "region_time_zone"],
        },
        "list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "gacha_id": {"type": "string", "description": "卡池 Id"},
                    "gacha_type": {
                        "type": "string",
                        "description": "卡池类型",
                        "enum": ["1", "2", "11", "12"],
                    },
                    "item_id": {"type": "string", "description": "物品 Id"},
                    "count": {"type": "string", "description": "数量，通常为1"},
                    "time": {
                        "type": "string",
                        "description": "获取物品的时间，应为「抽卡记录网页上显示的原始时间字符串」而非任何转换过的值。如果设备时区与服务器时区不一致，任意类型转换将会导致时区转换出现误差（除非应用进行了特殊处理）。",
                    },
                    "name": {"type": "string", "description": "物品名称"},
                    "item_type": {"type": "string", "description": "物品类型"},
                    "rank_type": {"type": "string", "description": "物品星级"},
                    "id": {"type": "string", "description": "内部 Id"},
                },
                "required": ["gacha_id", "gacha_type", "item_id", "time", "id"],
            },
            "description": "包含卡池记录",
        },
    },
    "required": ["info", "list"],
}

uigf22 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "info": {
            "type": "object",
            "properties": {
                "uid": {"type": "string", "pattern": "^\\d{9}$"},
                "lang": {
                    "type": "string",
                },
            },
            "required": ["uid", "lang"],
        },
        "list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "gacha_type": {"type": "string", "pattern": "^\\d{3}$"},
                    "item_id": {"type": "string"},
                    "count": {"type": "string", "pattern": "^\\d+$"},
                    "time": {"type": "string", "format": "date-time"},
                    "name": {"type": "string"},
                    "item_type": {"type": "string"},
                    "rank_type": {"type": "string", "pattern": "^\\d$"},
                    "id": {"type": "string", "pattern": "^\\d+$"},
                    "uigf_gacha_type": {"type": "string", "pattern": "^\\d{3}$"},
                },
                "required": [
                    "gacha_type",
                    "count",
                    "time",
                    "name",
                    "item_type",
                    "rank_type",
                    "id",
                    "uigf_gacha_type",
                ],
            },
        },
    },
    "required": ["info", "list"],
}

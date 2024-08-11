import os
import json
import schema
import time
from jsonschema import validate
import conv


def get_valid_file_path():
    while True:
        file_path = input("请输入你的旧版本文件路径：")
        if not os.path.exists(file_path):
            print("文件不存在，请重新输入")
        elif os.path.isdir(file_path):
            print("输入的不是文件路径，请重新输入")
        else:
            return file_path


def main():
    file_format = schema.uigf3
    file_version = ""
    output = {}

    output["info"] = {
        "export_timestamp": int(time.time()),
        "export_app": "UIGF-Upgrader-MoYan",
        "export_app_version": "1.0.1",
        "version": "v4.0",
    }

    old_file_path = get_valid_file_path()

    try:
        with open(old_file_path, "r", encoding="utf-8") as file:
            old_file = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("无法读取文件或文件格式不正确")
        exit(1)

    if "info" in old_file:
        if "version" in old_file["info"]:
            print("为UIGF-4.0版本，无需转换")
        elif "uigf_version" in old_file["info"]:
            uigf_version = old_file["info"]["uigf_version"][1:]
            if uigf_version == "3.0":
                file_format = schema.uigf3
                file_version = "uigf24p"

            elif uigf_version == "2.4":
                file_format = schema.uigf24
                file_version = "uigf24p"

            elif uigf_version == "2.3":
                file_format = schema.uigf23
                file_version = "uigf23"

        elif "srgf_version" in old_file["info"]:
            file_format = schema.srgf
            file_version = "srgf"
        else:
            file_format = schema.uigf22
            file_version = "uigf22"

    try:
        validate(instance=old_file, schema=file_format)
    except Exception as e:
        print("数据验证错误：", e)
        exit(1)

    handle = getattr(conv, file_version)
    output = handle(old_file, output)

    try:
        with open(old_file_path, "w", encoding="utf-8") as outfile:
            json.dump(output, outfile, indent=4, ensure_ascii=False)
        print("文件已成功升级和保存")
    except IOError:
        print("保存文件时出现错误")


if __name__ == "__main__":
    main()

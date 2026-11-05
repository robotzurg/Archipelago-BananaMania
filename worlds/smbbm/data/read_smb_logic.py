import csv
import json

CSV_LOGIC_ORDER = [
    "W1",
    "W2",
    "W3",
    "W4",
    "W5",
    "W6",
    "W7",
    "W8",
    "W9",
    "W10",
    "Deluxe",
    "SMB1 Challenge Mode Logic",
    "Reverse Mode",
    "Dark Banana Mode",
    "Golden Banana Mode",
    "Original Stages Mode",
    "SMB1 Casual",
    "SMB1 Normal",
    "SMB1 Expert",
    "SMB1 Master",
    "SMB2 Casual EX",
    "SMB2 Normal EX",
    "SMB2 Expert EX",
    "SMB2 Master EX"
]

def main():  

    world_tracker_idx = 0
    logic_dict: dict[str, list[dict]] = dict()
    logic_dict[CSV_LOGIC_ORDER[world_tracker_idx]] = []

    headers = []
    level_idx = 0
    data_length = 7
    base_loc_id = 1
    
    with open('logic.csv') as csvfile:
        logic_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for idx, row in enumerate(logic_reader):
            if idx == 0:
                headers = row[0:7]
                print(headers)
                continue
            try:
                if row[0] == "":
                    world_tracker_idx += 1

                    if world_tracker_idx > 9:
                        data_length = 7

                    logic_dict[CSV_LOGIC_ORDER[world_tracker_idx]] = []
                    level_idx = 0
                    continue
                elif "Level Name" in row[0] or "Difficulty" in row[0]:
                    continue
            except:
                pass

            logic_dict[CSV_LOGIC_ORDER[world_tracker_idx]].append({})

            for idx, data in enumerate(row[0:data_length]):
                if data == "None":
                    data = ""
                if data == "\u2714":
                    data = "Y"
                if "<" in data or ">" in data:
                    data = data.replace("<", "").replace(">", "")
                if "seconds" in data:
                    data = data.replace(" seconds", "")

                if "Items" in headers[idx]:
                    data = data.split(" + ")

                logic_dict[CSV_LOGIC_ORDER[world_tracker_idx]][level_idx]["id"] = (base_loc_id * (world_tracker_idx + 1) * 1000) + ((level_idx) * 10)
                logic_dict[CSV_LOGIC_ORDER[world_tracker_idx]][level_idx][headers[idx]] = data

            level_idx += 1

    json_str = json.dumps(logic_dict, indent=4)
    with open("logic.json", "w") as f:
        f.write(json_str)

if __name__ == '__main__':
    main()
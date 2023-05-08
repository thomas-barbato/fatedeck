import os
import glob
from datetime import datetime
import pytz

tz_FR = pytz.timezone("Europe/Paris")
datetime_FR = datetime.now(tz_FR)
datatime_now = datetime_FR.strftime("%Y-%d-%m %H:%M:%S")

get_cwd = os.getcwd()
cards_array = [element.split("\\")[-1] for element in glob.glob(get_cwd + "/*.svg")]
i = 1

with open("D:\\wamp64\\www\\malifaux-fate-gen\\malifaux\\backend\\fixtures\cards.json", "a") as file:
    file.write("[\n")
    for card in cards_array:
        file.write("\t{\n")
        file.write('\t"model": "backend.cards",')
        file.write("\n")
        file.write('\t"pk": null,')
        file.write('\n\t"fields": {\n')
        file.write('\t\t"name": "{0}", \n'.format(card.split(".")[0]))
        file.write('\t\t"filename": "{0}", \n'.format(card))
        file.write('\t\t"created_at": "{0}", \n'.format(datatime_now))
        file.write('\t\t"updated_at": "{0}", \n'.format(datatime_now))
        file.write('\t\t"deleted_at": null \n')
        file.write("\t\t}")
        if i < len(cards_array):
            file.write("\n\t},\n")
        else:
            file.write("\n}")
        i += 1
    file.write("\n]")

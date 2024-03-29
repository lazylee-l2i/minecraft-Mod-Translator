import zipfile
import glob
import json
import shutil
import commentjson
import googletrans

class JsonExporter:
    def __init__(self) -> None:
        self.mod_list = glob.glob("./mod/*.jar")
        self.translated_list = glob.glob("./translated_mod/*.jar")
        self.translator = googletrans.Translator()

    def oneFile(self, _file):
        result = self.postProcessing(_file=_file)
        if result is not None:
            json_file, lang_path = result
            result_json = self.translate(_json_data=json_file)
            self.saveJar(result_json, _file, lang_path)

    def allFile(self):
        for file in self.mod_list:
            zip_path = file.replace("mod", "translated_mod")
            if zip_path in self.translated_list:
                continue
            zip_path = zip_path.replace(".jar", "_korean.jar")
            shutil.copy(file, zip_path)
            self.oneFile(zip_path)

    def postProcessing(self, _file :str="jar_file"):
        json_file = "json_file"
        file_list = zipfile.ZipFile(_file, 'r')
        for _file in file_list.namelist():
            if "en_us.json" in _file:
                print(_file)
                try:
                    json_file = json.loads(file_list.read(_file))
                except:
                    json_file = commentjson.loads(file_list.read(_file))
                    
                file_list.close()
                return json_file ,_file
        print("Here is no Language file")

    def translate(self, _json_data :dict="Json File"):
        result = _json_data.copy()
        for _key in _json_data.keys():
            try:
                result[_key] = self.translator.translate(_json_data[_key], src="en", dest="ko").text
            except:
                print("아 걱정마세요. 평범한 에러메세지입니다. 무료버전의 한계니 그냥 넘어가도록하죠.")
                result[_key] = _json_data[_key]
        return result

    def saveJar(self, _result_json :dict, _zip_path :str, _lang_path :str):
        t_jar = zipfile.ZipFile(_zip_path, 'a')
        t_jar.writestr(_lang_path.replace("en_us", "ko_kr"), json.dumps(_result_json, indent=4, ensure_ascii=False))
        t_jar.close()


def run():
    je = JsonExporter()
    je.allFile()


if __name__ == "__main__":
    run()

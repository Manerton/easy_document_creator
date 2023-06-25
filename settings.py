import json


class Settings:
    __slots__ = (
        "MONGO_URI",
        "UPLOAD_FOLDER",
        "HOST",
        "PORT"
    )

    def __init__(self):
        try:
            settings_config = "appsetting.json"
            settings_list = json.load(open(settings_config, "r"))
            for setting_key in settings_list:
                setattr(self, setting_key, settings_list[setting_key])

            list(getattr(self, attr) for attr in self.__slots__)

        except IndexError as exc:
            print("No config found. Exception: ", exc)
        except FileNotFoundError as exc:
            print("File not found. Exception: ", exc)
        except AttributeError as exc:
            print("Wrong setting provided. Exception: ", exc)


settings = Settings()

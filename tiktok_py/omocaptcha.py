import httpx
import time
import base64


class OMOCaptcha:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.job_id = None

    def get_result(self):
        while True:
            r = httpx.post("https://omocaptcha.com/api/getJobResult", json={
            "api_token": self.api_key,
            "job_id": self.job_id
            })
            if r.json()["status"] == "waiting":
                time.sleep(1)
            elif r.json()["status"] == "fail":
                raise Exception()
            elif r.json()["status"] == "success":
                return r.json()["result"]

    def solve_tiktok_2objects(self, image_url: str, width: int, height: int):
        image_content = httpx.get(image_url).content
        r = httpx.post("https://omocaptcha.com/api/createJob", json={
            "api_token": self.api_key,
            "data": {
                "type_job_id": 22,
                "image_base64": base64.b64encode(image_content).decode("utf-8"),
                "width_view": width,
                "height_view": height,
            }
        })
        if r.json()["error"]:
            raise Exception(r.json()["message"])
        self.job_id = r.json()["job_id"]
        result = self.get_result()
        return float(result.split("|")[0]), float(result.split("|")[1]), float(result.split("|")[2]), float(result.split("|")[3])

    def solve_tiktok_rotation(self, outer_image_url: str, inner_image_url: str):
        r = httpx.post("https://omocaptcha.com/api/createJob", json={
            "api_token": self.api_key,
            "data": {
                "type_job_id": 23,
                "image_base64": f"{base64.b64encode(httpx.get(inner_image_url).content).decode('utf-8')}|{base64.b64encode(httpx.get(outer_image_url).content).decode('utf-8')}",
            }
        })
        if r.json()["error"]:
            raise Exception(r.json()["message"])
        self.job_id = r.json()["job_id"]
        result = self.get_result()
        return int(result)

    def solve_tiktok_drag_drop(self, image_url: str, width: int):
        image_content = httpx.get(image_url).content
        r = httpx.post("https://omocaptcha.com/api/createJob", json={
            "api_token": self.api_key,
            "data": {
                "type_job_id": 24,
                "image_base64": base64.b64encode(image_content).decode("utf-8"),
                "width_view": width
            }
        })
        if r.json()["error"]:
            raise Exception(r.json()["message"])
        self.job_id = r.json()["job_id"]
        result = self.get_result()
        return int(result)

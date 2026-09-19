import json
from typing import Dict, Any

import allure
import requests
from requests import Response

from config.settings import settings
from utils.logger import logger


class RequestBase:

    def __init__(self, base_url=None):
        self.base_url = base_url or settings.GATEWAY_URL
        self.timeout = settings.REQUEST_TIMEOUT
        self.retry_times = settings.RETRY_TIMES
        self.session = requests.Session()

    def _build_headers(self, need_auth=True, extra_headers=None):
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
        }
        if need_auth:
            token = settings.TEST_TOKEN
            if not token.startswith("Bearer "):
                token = f"Bearer {token}"
            headers["Authorization"] = token
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _full_url(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _log_request(self, method, url, **kwargs):
        logger.info(
            f"[请求] {method.upper()} {url}\n"
            f"  params={kwargs.get('params')}\n"
            f"  body={kwargs.get('json') or kwargs.get('data')}\n"
            f"  headers={self._mask_headers(kwargs.get('headers', {}))}"
        )

    def _log_response(self, resp):
        try:
            body = resp.json()
        except Exception:
            body = resp.text[:1000]
        logger.info(
            f"[响应] status={resp.status_code} time={resp.elapsed.total_seconds():.3f}s\n"
            f"  body={body}"
        )

    @staticmethod
    def _mask_headers(headers):
        masked = dict(headers)
        if "Authorization" in masked:
            val = masked["Authorization"]
            masked["Authorization"] = val[:10] + "***" + val[-6:] if len(val) > 16 else "***"
        return masked

    def _attach_allure(self, method, url, resp, **kwargs):
        req_body = json.dumps(kwargs.get("json") or kwargs.get("data") or {},
                              ensure_ascii=False, indent=2)
        try:
            resp_body = json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            resp_body = resp.text
        allure.attach(
            f"{method.upper()} {url}\nParams: {kwargs.get('params')}\nBody:\n{req_body}",
            name="Request",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            f"Status: {resp.status_code} | Time: {resp.elapsed.total_seconds():.3f}s\n"
            f"Body:\n{resp_body}",
            name="Response",
            attachment_type=allure.attachment_type.JSON,
        )

    def _request(self, method, path, need_auth=True, extra_headers=None, **kwargs):
        url = self._full_url(path)
        headers = self._build_headers(need_auth=need_auth, extra_headers=extra_headers)
        kwargs.setdefault("timeout", self.timeout)
        kwargs["headers"] = headers

        last_exc = None
        for attempt in range(1, self.retry_times + 1):
            try:
                self._log_request(method, url, **kwargs)
                resp = self.session.request(method, url, **kwargs)
                self._log_response(resp)
                self._attach_allure(method, url, resp, **kwargs)
                resp.raise_for_status()
                try:
                    return resp.json()
                except ValueError:
                    return {
                        "code": resp.status_code,
                        "message": resp.text,
                        "data": resp.text,
                    }
            except requests.HTTPError as e:
                last_exc = e
                logger.warning(f"第 {attempt} 次请求 HTTP 异常: {e}，响应: {getattr(e.response, 'text', '')[:500]}")
                if 400 <= (e.response.status_code if e.response else 999) < 500:
                    break
            except requests.RequestException as e:
                last_exc = e
                logger.warning(f"第 {attempt} 次请求异常: {e}")
            if attempt < self.retry_times:
                import time
                time.sleep(1)

        return {
            "code": -1,
            "message": f"请求失败: {last_exc}",
            "data": None,
        }

    def get(self, path, params=None, need_auth=True, extra_headers=None):
        return self._request("get", path, need_auth=need_auth,
                             extra_headers=extra_headers, params=params)

    def post(self, path, json_body=None, data=None, params=None,
             need_auth=True, extra_headers=None):
        return self._request("post", path, need_auth=need_auth,
                             extra_headers=extra_headers,
                             json=json_body, data=data, params=params)

    def put(self, path, json_body=None, data=None, params=None,
            need_auth=True, extra_headers=None):
        return self._request("put", path, need_auth=need_auth,
                             extra_headers=extra_headers,
                             json=json_body, data=data, params=params)

    def delete(self, path, params=None, json_body=None, need_auth=True, extra_headers=None):
        return self._request("delete", path, need_auth=need_auth,
                             extra_headers=extra_headers,
                             params=params, json=json_body)


request_base = RequestBase()

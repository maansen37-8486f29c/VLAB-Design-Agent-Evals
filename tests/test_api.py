"""API端点测试：不需要Dify额度，也不依赖公网。"""
import unittest
from fastapi.testclient import TestClient
from main import app


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_requirement_f01(self):
        r = self.client.get("/tools/requirement", params={"requirement_id": "HARD-F01"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["found"])
        self.assertEqual(r.json()["id"], "HARD-F01")

    def test_requirement_unknown(self):
        r = self.client.get("/tools/requirement", params={"requirement_id": "HARD-F99"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["found"])

    def test_explicit_conflicts(self):
        r = self.client.post("/tools/assess-front-design",json={
            "proposal":"散热格栅取消，将原有的双层圆盘结构简化成单层装饰盖。"
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual({v["id"] for v in r.json()["violations"]}, {"HARD-F01","HARD-F02"})

    def test_non_conflict_is_not_certification(self):
        r = self.client.post("/tools/assess-front-design",json={
            "proposal":"保留双层圆盘结构和散热格栅。"
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"],"no_explicit_conflict_detected")
        self.assertIn("未评估",r.json()["engineering_compliance"])

    def test_blank_proposal_rejected(self):
        r = self.client.post("/tools/assess-front-design",json={"proposal":""})
        self.assertEqual(r.status_code,422)

    def test_parameter_does_not_fabricate_value(self):
        r = self.client.get("/tools/verified-parameter",params={"parameter":"散热格栅最小面积"})
        self.assertEqual(r.status_code,200)
        self.assertFalse(r.json()["verified"])
        self.assertIsNone(r.json()["value"])

    def test_dify_schema_has_three_tools_and_server(self):
        r = self.client.get("/dify-openapi.json")
        self.assertEqual(r.status_code,200)
        data = r.json()
        self.assertEqual(data["openapi"],"3.0.3")
        operation_ids = {
            data["paths"]["/tools/requirement"]["get"]["operationId"],
            data["paths"]["/tools/assess-front-design"]["post"]["operationId"],
            data["paths"]["/tools/verified-parameter"]["get"]["operationId"],
        }
        self.assertEqual(operation_ids,{"lookup_requirement","assess_front_design","lookup_verified_parameter"})
        self.assertEqual(data["servers"][0]["url"],"http://testserver")


if __name__ == "__main__":
    unittest.main()

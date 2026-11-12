import unittest
from src.requirements_tool import (
    lookup_requirement, assess_front_design, lookup_verified_parameter, dispatch_tool
)


class RequirementsToolTests(unittest.TestCase):
    def test_lookup_hard_f01(self):
        result=lookup_requirement("HARD-F01")
        self.assertTrue(result["found"])
        self.assertIn("双层圆盘", result["rule"])
        self.assertIn("必须完整保留", result["rule"])

    def test_lookup_hard_f02(self):
        result=lookup_requirement("HARD-F02")
        self.assertTrue(result["found"])
        self.assertIn("散热格栅不能取消", result["rule"])

    def test_detect_two_explicit_violations(self):
        r=assess_front_design("散热格栅取消，将原有的双层圆盘结构简化成单层装饰盖。")
        self.assertEqual(r["status"], "explicit_requirement_conflict")
        self.assertEqual({v["id"] for v in r["violations"]}, {"HARD-F01","HARD-F02"})

    def test_preserving_components_is_not_declared_compliant(self):
        r=assess_front_design("保留双层圆盘结构，并保留散热格栅，其他条件尚待验证。")
        self.assertEqual(r["status"], "no_explicit_conflict_detected")
        self.assertIn("未评估",r["engineering_compliance"])

    def test_missing_dimensions_do_not_hallucinate(self):
        r=lookup_verified_parameter("散热格栅最低通风面积（平方厘米）")
        self.assertFalse(r["verified"])
        self.assertIsNone(r["value"])

    def test_unknown_requirement_is_not_fabricated(self):
        r=lookup_requirement("HARD-F99")
        self.assertFalse(r["found"])

    def test_dispatch_unknown_tool(self):
        r=dispatch_tool("send_secret", {})
        self.assertEqual(r["error"], "unknown_tool")


if __name__ == "__main__": unittest.main()

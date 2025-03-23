# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Union

import akshare as ak
import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Bond data mcp server")


def format_bond_curve_data(curve_name: str, bond_yield_curve: pd.DataFrame) -> Dict[str, Any]:
    min_date = bond_yield_curve["日期"].min().strftime("%Y-%m-%d")
    max_date = bond_yield_curve["日期"].max().strftime("%Y-%m-%d")

    result = {
        "metadata": {
            "curve_name": curve_name,
            "time_range": [min_date, max_date],
            "currency": "CNY",
        },
        "series": {},
    }

    terms = [col for col in bond_yield_curve.columns if col != "日期"]

    for term in terms:
        series_df = bond_yield_curve[["日期", term]].copy()
        series_df["date_str"] = series_df["日期"].dt.strftime("%Y%m%d")
        daily_data = [{"date": row["date_str"], "yield": row[term]} for _, row in series_df.iterrows()]

        values = series_df[term]
        stats = {
            "max": {
                "value": float(values.max()),
                "date": series_df.loc[values.idxmax(), "date_str"],
            },
            "min": {
                "value": float(values.min()),
                "date": series_df.loc[values.idxmin(), "date_str"],
            },
            "mean": round(float(values.mean()), 4),
            "median": round(float(values.median()), 4),
            "variance": round(float(values.var(ddof=0)), 6),
            "std_dev": round(float(values.std(ddof=0)), 4),
            "quantiles": {
                "q1": round(float(values.quantile(0.25)), 4),
                "q3": round(float(values.quantile(0.75)), 4),
            },
        }

        result["series"][term] = {"daily_data": daily_data, "statistics": stats}

    if len(terms) > 1:
        result["analysis"] = {}
        result["analysis"]["correlation"] = {}
        corr_matrix = bond_yield_curve[terms].corr().round(3)
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                key = f"{terms[i]}_{terms[j]}"
                result["analysis"]["correlation"][key] = float(corr_matrix.iloc[i, j])

    return result


@mcp.tool()
def get_china_bond_curve(
    bond_curve_name: str = "中债国债收益率曲线",
    term_list: Union[List[str], str] = "10年",
    start_date: Union[str, int] = "20250101",
    end_date: Union[str, int] = "20250105",
) -> Dict[str, Any]:
    """从中国债券信息网获取国债及其他债券收益率曲线数据并进行统计分析.

    Parameters
    ----------
    bond_curve_name : str, default="中债国债收益率曲线"
        债券曲线名称,可选值包括:
        - "中债国债收益率曲线"
        - "中债中短期票据收益率曲线(AAA)"
        - "中债商业银行普通债收益率曲线(AAA)"
    term_list : Union[List[str], str], default="10年"
        债券曲线期限,可以是单个期限字符串或期限列表
        可选值包括: "3月", "6月", "1年", "3年", "5年", "7年", "10年", "30年"
    start_date : Union[str, int], default="20250101"
        收益率曲线开始日期,格式为"YYYYMMDD"
        例如"20250101"代表2025年1月1日
    end_date : Union[str, int], default="20250105"
        收益率曲线结束日期,格式为"YYYYMMDD"
        例如"20250105"代表2025年1月5日

    Returns
    -------
    Dict[str, Any]
        包含债券曲线数据和统计分析的结构化字典

        成功时返回格式::

            {
                "metadata": {
                    "curve_name": "债券曲线名称",
                    "time_range": ["起始日期", "结束日期"],
                    "currency": "CNY"
                },
                "series": {
                    "期限1": {
                        "daily_data": [
                            {"date": "日期字符串", "yield": 收益率值},
                            ...
                        ],
                        "statistics": {
                            "max": {"value": 最大值, "date": "最大值日期"},
                            "min": {"value": 最小值, "date": "最小值日期"},
                            "mean": 平均值,
                            "median": 中位数,
                            "variance": 方差,
                            "std_dev": 标准差,
                            "quantiles": {"q1": 25%分位数, "q3": 75%分位数}
                        }
                    },
                    "期限2": {...}
                },
                "analysis": {  # 仅当请求多个期限时存在
                    "correlation": {
                        "期限1_期限2": 相关系数,
                        ...
                    }
                }
            }

        失败时返回格式::

            {
                "error": "错误信息"
            }

    返回数据示例:
    {
        'metadata': {
            'currency': 'CNY',
            'curve_name': '中债国债收益率曲线',
            'time_range': ['2025-01-02', '2025-01-03']
        },
        'series': {
            '10年': {
                'daily_data': [
                    {'date': '20250102', 'yield': 1.6077},
                    {'date': '20250103', 'yield': 1.6041}
                ],
                'statistics': {
                    'max': {'date': '20250102', 'value': 1.6077},
                    'mean': 1.6059,
                    'median': 1.6059,
                    'min': {'date': '20250103', 'value': 1.6041},
                    'quantiles': {'q1': 1.605, 'q3': 1.6068},
                    'std_dev': 0.0018,
                    'variance': 0.000003
                }
            }
        }
    }

    Notes
    -----
    - end_date与start_date之间的时间间隔建议小于一年,避免数据量过大
    - 收益率数据单位为百分比,如1.6077表示1.6077%
    - "中债中短期票据收益率曲线(AAA)"没有"30年"期限的数据
    - 不同债券曲线名称可能具有不同的期限可用性,请根据实际情况选择合适的期限
    - 当请求多个期限时,会自动计算期限之间的相关系数

    Raises
    ------
    Exception
        当API调用失败、数据处理出错或提供的参数无效时可能引发异常,
        但这些异常会被捕获并作为错误信息返回
    """
    assert bond_curve_name in [
        "中债国债收益率曲线",
        "中债中短期票据收益率曲线(AAA)",
        "中债商业银行普通债收益率曲线(AAA)",
    ]

    if isinstance(term_list, str):
        term_list = [term_list]

    for term in term_list:
        assert term in ["3月", "6月", "1年", "3年", "5年", "7年", "10年", "30年"]

    if bond_curve_name == "中债中短期票据收益率曲线(AAA)":
        assert "30年" not in term_list

    if start_date is not None and isinstance(start_date, int):
        start_date = str(start_date)
    if end_date is not None and isinstance(end_date, int):
        end_date = str(end_date)

    try:
        bond_china_yield_df = ak.bond_china_yield(start_date=start_date, end_date=end_date)
        if bond_china_yield_df.empty:
            return {"error": f"No data available for the specified date range: {start_date} to {end_date}"}

        bond_yield_curve = bond_china_yield_df[bond_china_yield_df["曲线名称"] == bond_curve_name].copy()
        bond_yield_curve = bond_yield_curve[["日期"] + term_list]
        bond_yield_curve["日期"] = bond_yield_curve["日期"].astype("datetime64[ns]")

        return format_bond_curve_data(bond_curve_name, bond_yield_curve)
    except Exception as e:
        return {"error": f"Failed to retrieve data: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")

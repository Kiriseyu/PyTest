# group_recommendations.py
import pandas as pd

def group_recommendations(df: pd.DataFrame, output_file: str):
    """
    给出并绘制各分组推荐检测时点
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    # 假设推荐检测时点的算法
    df['推荐检测时点'] = df['检测孕周'].apply(lambda x: x + 4 if x < 28 else x + 2)

    # 保存推荐检测时点
    df[['孕妇代码', '推荐检测时点']].to_excel(output_file, index=False)
    print(f"各分组推荐检测时点已保存：{output_file}")

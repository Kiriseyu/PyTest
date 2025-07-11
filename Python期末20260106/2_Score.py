score = float(input())
if score >= 85 and score <= 100:
    ans = "优秀"
elif score >= 70 and score <= 85:
    ans = "良好"
elif score >= 60 and score <= 70:
    ans = "合格"
elif score >= 0 and score <= 60:
    ans = "不合格"
else:
    ans = "成绩无效"
print(ans)
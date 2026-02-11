import streamlit as st
import pandas as pd
import io

# ---------------- تنظیمات صفحه ----------------
st.set_page_config(
    page_title="تحلیل بسته‌بندی، ضایعات و سودآوری",
    layout="wide"
)

st.title("📦 تحلیل کامل بسته‌بندی و درصد درجات کاشی")
st.write("محاسبه درصد هر درجه کاشی و انواع ضایعات نسبت به تولید کوره")

# ---------------- پارامترهای اقتصادی ----------------
st.sidebar.header("⚙️ پارامترهای اقتصادی")

cost_per_m2 = st.sidebar.number_input(
    "هزینه تولید هر متر مربع (تومان)",
    value=220000,
    step=10000
)

price_grade1 = st.sidebar.number_input(
    "قیمت فروش درجه 1 (تومان)",
    value=400000,
    step=10000
)

grade_factor = {
    "درجه 2": 0.85,
    "درجه 3": 0.70,
    "درجه 4": 0.50,
    "درجه 5": 0.30
}

# ---------------- آپلود فایل ----------------
uploaded_file = st.file_uploader("📁 فایل اکسل را بارگذاری کنید", type=["xlsx"])

if uploaded_file:
    try:
        kiln_df = pd.read_excel(uploaded_file, sheet_name="کوره ")
        pack_df = pd.read_excel(uploaded_file, sheet_name="بسته بندی ")

        sizes = ["60*60", "60*120"]
        report = []

        for size in sizes:
            kiln_output = kiln_df.loc[
                kiln_df["سایز"] == size,
                "متراژ تولیدی"
            ].sum()

            pack = pack_df[pack_df["سایز"] == size]

            deg2 = pack["درجه 2"].sum()
            deg3 = pack["درجه 3"].sum()
            deg4 = pack["درجه 4"].sum()
            deg5 = pack["درجه 5"].sum()

            waste_normal = pack["ضایعات معمولی"].sum()
            waste_special = pack["ضایعات ویژه"].sum()
            waste_2 = pack["ضایعات 2"].sum()

            total_waste = waste_normal + waste_special + waste_2

            def percent(x):
                return round((x / kiln_output) * 100, 2) if kiln_output > 0 else 0

            # درآمد و سود
            revenue = (
                deg2 * price_grade1 * grade_factor["درجه 2"]
                + deg3 * price_grade1 * grade_factor["درجه 3"]
                + deg4 * price_grade1 * grade_factor["درجه 4"]
                + deg5 * price_grade1 * grade_factor["درجه 5"]
            )

            total_cost = kiln_output * cost_per_m2
            profit = revenue - total_cost

            report.append({
                "سایز": size,
                "تولید کوره (متر مربع)": kiln_output,

                "درصد درجه 2": percent(deg2),
                "درصد درجه 3": percent(deg3),
                "درصد درجه 4": percent(deg4),
                "درصد درجه 5": percent(deg5),

                "درصد ضایعات معمولی": percent(waste_normal),
                "درصد ضایعات ویژه": percent(waste_special),
                "درصد ضایعات درجه 2": percent(waste_2),
                "درصد کل ضایعات": percent(total_waste),

                "درآمد فروش (تومان)": round(revenue),
                "هزینه تولید (تومان)": round(total_cost),
                "سود / زیان (تومان)": round(profit)
            })

        df = pd.DataFrame(report)

        # ---------------- جدول ----------------
        st.subheader("📋 جدول درصد درجات و ضایعات بسته‌بندی")
        st.dataframe(df, use_container_width=True)

        # ---------------- نمودار درصدها ----------------
        st.subheader("📊 مقایسه درصد ضایعات")
        st.bar_chart(
            df.set_index("سایز")[
                ["درصد ضایعات معمولی", "درصد ضایعات ویژه", "درصد ضایعات درجه 2"]
            ]
        )

        # ---------------- تحلیل متنی ----------------
        st.subheader("📝 تحلیل بسته‌بندی")

        worst = df.loc[df["درصد کل ضایعات"].idxmax()]

        analysis = f"""
بررسی نتایج بسته‌بندی نشان می‌دهد سایز **{worst['سایز']}**
بیشترین درصد ضایعات را به خود اختصاص داده است.

تفکیک ضایعات نشان می‌دهد که ضایعات معمولی و ضایعات درجه 2
سهم قابل توجهی در افت بازده نهایی تولید دارند.

افزایش کنترل کیفی در مرحله بسته‌بندی و بازنگری در
معیارهای درجه‌بندی می‌تواند منجر به کاهش ضایعات
و افزایش سودآوری کارخانه گردد.
"""
        st.write(analysis)

        # ---------------- خروجی اکسل ----------------
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Packaging_Report")

        st.download_button(
            "⬇️ دانلود گزارش بسته‌بندی (اکسل)",
            data=output.getvalue(),
            file_name="packaging_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("❌ خطا در پردازش فایل")
        st.write(e)

else:
    st.info("⬆️ لطفاً فایل اکسل را بارگذاری کنید")

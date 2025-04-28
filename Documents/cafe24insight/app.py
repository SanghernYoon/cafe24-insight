import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import io

st.set_page_config(page_title="Cafe24 쇼핑몰 인사이트", page_icon="🛒", layout="centered")

st.title("🛒 Cafe24 쇼핑몰 인사이트")
st.write("""
운영 중인 쇼핑몰 주소를 입력하면, 사이트의 상태를 분석하고  
**Cafe24**가 제공하는 맞춤형 개선 인사이트를 안내해드립니다.
""")

API_KEY = "AIzaSyBo2LdoFNFxphORUYH9beG1TqDn-AFG_II"  # ← 여기에 본인 Google PageSpeed API 키를 입력하세요!

url = st.text_input("분석할 쇼핑몰 주소를 입력하세요 (예: https://www.mysite.com)")

def get_site_info(url):
    try:
        resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "제목 없음"
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc = desc_tag["content"].strip() if desc_tag and "content" in desc_tag.attrs else "설명 없음"
        return title, desc
    except Exception as e:
        return "정보를 가져올 수 없음", "설명을 가져올 수 없음"

def get_pagespeed_score(url, api_key):
    try:
        api_url = (
            f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            f"?url={url}&key={api_key}&strategy=mobile"
        )
        resp = requests.get(api_url, timeout=100)
        data = resp.json()
        if "error" in data:
            st.error(f"API 오류: {data['error'].get('message', '알 수 없는 오류')}")
            st.json(data['error'])
            return None
        score = int(data['lighthouseResult']['categories']['performance']['score'] * 100)
        return score
    except Exception as e:
        st.error(f"예외 발생: {e}")
        return None

def make_pdf(title, desc, score, url):
    pdf = FPDF()
    pdf.add_page()
    # NanumGothicCoding 폰트 등록 (TTF 파일이 같은 폴더에 있어야 함)
    pdf.add_font('NanumGothicCoding', '', 'NanumGothicCoding.ttf', uni=True)
    pdf.set_font('NanumGothicCoding', '', 16)
    pdf.cell(0, 10, "Cafe24 쇼핑몰 인사이트 분석 리포트", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('NanumGothicCoding', '', 12)
    pdf.cell(0, 10, f"분석 대상: {url}", ln=True)
    pdf.cell(0, 10, f"사이트 제목: {title}", ln=True)
    pdf.multi_cell(0, 10, f"사이트 설명: {desc}")
    pdf.ln(5)
    pdf.cell(0, 10, f"모바일 최적화 점수: {score}점", ln=True)
    pdf.cell(0, 10, "사이트 속도: 60점", ln=True)
    pdf.cell(0, 10, "UI/UX: 50점", ln=True)
    pdf.cell(0, 10, "결제수단 다양성: 40점", ln=True)
    pdf.ln(5)
    pdf.set_font('NanumGothicCoding', '', 12)
    pdf.cell(0, 10, "개선 인사이트 및 Cafe24 제안:", ln=True)
    if score < 80:
        pdf.cell(0, 10, "- 모바일 최적화가 부족합니다. Cafe24의 반응형 테마를 도입해보세요!", ln=True)
    else:
        pdf.cell(0, 10, "- 모바일 최적화가 우수합니다.", ln=True)
    pdf.cell(0, 10, "- Cafe24 CDN 서비스로 사이트 속도 개선", ln=True)
    pdf.cell(0, 10, "- Cafe24 간편결제 연동으로 결제수단 다양화", ln=True)
    return pdf

if st.button("분석하기") and url:
    st.success(f"분석 대상: {url}")

    # 실제 사이트 정보 가져오기
    title, desc = get_site_info(url)
    st.markdown(f"**사이트 제목:** {title}")
    st.markdown(f"**사이트 설명:** {desc}")

    # 실제 모바일 최적화 점수 가져오기
    score = get_pagespeed_score(url, API_KEY)
    if score is None:
        score = 65

    # 카드 형태로 분석 결과 표시
    st.markdown("### 📝 분석 결과 요약")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 📱 모바일 최적화")
        st.progress(score / 100)
        st.markdown(f"**{score}점**")
    with col2:
        st.markdown("#### ⚡ 사이트 속도")
        st.progress(0.6)
        st.markdown("**60점**")
    with col3:
        st.markdown("#### 🎨 UI/UX")
        st.progress(0.5)
        st.markdown("**50점**")
    with col4:
        st.markdown("#### 💳 결제수단 다양성")
        st.progress(0.4)
        st.markdown("**40점**")

    # 인사이트 및 제안
    st.markdown("### 💡 개선 인사이트 및 Cafe24 제안")
    if score < 80:
        st.warning("모바일 최적화가 부족합니다. Cafe24의 반응형 테마를 도입해보세요!")
    else:
        st.success("모바일 최적화가 우수합니다.")
    st.info("✅ Cafe24 CDN 서비스로 사이트 속도 개선")
    st.info("✅ Cafe24 간편결제 연동으로 결제수단 다양화")

    # PDF 다운로드 버튼
    pdf = make_pdf(title, desc, score, url)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer = io.BytesIO(pdf_bytes)
    st.download_button(
        label="PDF로 결과 다운로드",
        data=pdf_buffer,
        file_name="cafe24_insight_report.pdf",
        mime="application/pdf"
    )

else:
    st.caption("예시: https://www.fashionmall.com")

st.markdown("---")
st.markdown("본 서비스는 데모 버전입니다. 실제 분석 결과는 참고용입니다.")
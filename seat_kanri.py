import streamlit as st
import pandas as pd
from datetime import date
import re
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# =========================
# 認証情報読み込み（あなたの形式）
# =========================
google_cloud_secret = st.secrets["google_cloud"]
service_account_info = {
    "type": google_cloud_secret["type"],
    "project_id": google_cloud_secret["project_id"],
    "private_key_id": google_cloud_secret["private_key_id"],
    "private_key": google_cloud_secret["private_key"],
    "client_email": google_cloud_secret["client_email"],
    "client_id": google_cloud_secret["client_id"],
    "auth_uri": google_cloud_secret["auth_uri"],
    "token_uri": google_cloud_secret["token_uri"],
    "auth_provider_x509_cert_url": google_cloud_secret["auth_provider_x509_cert_url"],
    "client_x509_cert_url": google_cloud_secret["client_x509_cert_url"],
    "universe_domain": google_cloud_secret.get("universe_domain", "googleapis.com"),
}

SHEET_ID = st.secrets.get("sheets", {}).get(
    "SHEET_ID", "1vRm5sRSDe4HoBX-Agot6naIkTY9mKz66QOVa5K_JaeQ"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ✅ ここが重要：oauth2client → google.oauth2.service_account に統一
@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID).sheet1  # ← 先頭シートを返す

sheet = get_sheet()  # ← あなたの形式と同じ



# ====== 小ユーティリティ ======
def clean_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s).replace("\u3000", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s


# ====== データ読み書き ======
@st.cache_data(ttl=60)
def load_df():
    df = get_as_dataframe(sheet, evaluate_formulas=True, dtype=None, header=0)
    df = df.dropna(how="all")

    cols = ["メーカー名", "部品番号", "板厚", "枚数", "最終更新日"]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[cols]

    df["メーカー名"] = df["メーカー名"].astype(str).map(clean_text)
    df["部品番号"] = df["部品番号"].astype(str).map(clean_text)
    df["枚数"] = pd.to_numeric(df["枚数"], errors="coerce").fillna(0).astype(int)
    df["板厚"] = pd.to_numeric(df["板厚"], errors="coerce")
    df["最終更新日"] = pd.to_datetime(df["最終更新日"], errors="coerce").dt.date
    return df


def save_df(df: pd.DataFrame):
    # 全消し→一括書き戻し（ヘッダ含む）
    sheet.clear()
    set_with_dataframe(sheet, df, include_index=False, include_column_header=True, resize=True)
    # 読み直しのためキャッシュ無効化
    st.cache_data.clear()


# ---------- アプリ本体 ----------
st.title("シート材在庫 管理アプリ")

df = load_df()
SOUSA = st.radio("操作を選択", ["材料の新規追加", "在庫の増減"], horizontal=True)

# 既存メーカー一覧（空文字除外）
maker_list = sorted(x for x in set(df["メーカー名"].dropna()) if clean_text(x))

if SOUSA == "材料の新規追加":
    st.subheader("材料の新規追加")

    name_choice = st.selectbox(
        "メーカー名を選択してください",
        ["選択してください", *maker_list, "その他メーカー"],
        index=0,
    )

    if name_choice == "その他メーカー":
        name = clean_text(st.text_input("新規メーカー名を入力してください"))
    else:
        name = "" if name_choice == "選択してください" else clean_text(name_choice)

    part = clean_text(st.text_input("部品番号を入力してください"))
    itaatu = st.number_input("板厚 (mm)", value=0.0, step=0.1, format="%.1f")
    maisuu = st.number_input("枚数を入力してください", value=0, step=1)
    send_date = st.date_input("登録日", value=date.today())

    if name and part:
        exist = df[(df["メーカー名"] == name) & (df["部品番号"] == part)]
        if not exist.empty:
            st.info(f"既存データあり：現在の枚数 {int(exist.iloc[0]['枚数'])}")

    if st.button("登録 / 反映", type="primary"):
        if not name or name == "選択してください":
            st.error("メーカー名を選択/入力してください")
        elif not part:
            st.error("部品番号を入力してください")
        else:
            mask = (df["メーカー名"] == name) & (df["部品番号"] == part)
            if mask.any():
                df.loc[mask, ["板厚", "枚数", "最終更新日"]] = [itaatu, int(maisuu), send_date]
            else:
                new_row = {
                    "メーカー名": name,
                    "部品番号": part,
                    "板厚": itaatu,
                    "枚数": int(maisuu),
                    "最終更新日": send_date,
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            save_df(df)
            st.success("保存しました！")

elif SOUSA == "在庫の増減":
    st.subheader("在庫の増減")

    maker_sel = st.selectbox(
        "メーカー名を選択して部品番号を絞り込み",
        ["選択してください", *maker_list],
        index=0,
    )

    if maker_sel == "選択してください":
        st.info("まずメーカー名を選んでください。")
        st.stop()

    maker_sel = clean_text(maker_sel)
    filtered = df[df["メーカー名"] == maker_sel].copy()

    def make_label(row):
        t = f" t{row['板厚']:.1f}mm" if pd.notna(row["板厚"]) else ""
        return f"{row['部品番号']}{t}"

    if filtered.empty:
        st.warning("このメーカーに紐づく部品がありません。")
        st.stop()

    filtered["__label__"] = filtered.apply(make_label, axis=1)

    buhin_label = st.selectbox(
        "部品番号を選択してください",
        ["選択してください"] + filtered["__label__"].tolist(),
        index=0,
    )

    if buhin_label != "選択してください":
        idx_preview = filtered.index[filtered["__label__"] == buhin_label]
        if len(idx_preview) > 0:
            ridx_preview = idx_preview[0]
            cur = int(df.loc[ridx_preview, "枚数"]) if pd.notna(df.loc[ridx_preview, "枚数"]) else 0
            st.caption(f"現在の在庫：{cur} 枚")

    change = st.number_input("増減枚数（入庫は正、出庫は負）", value=0, step=1)
    send_date = st.date_input("更新日", value=date.today())

    if st.button("在庫を更新", type="primary"):
        if buhin_label == "選択してください":
            st.error("部品番号を選択してください")
        elif change == 0:
            st.error("増減枚数を入力してください（正または負）")
        else:
            idx = filtered.index[filtered["__label__"] == buhin_label]
            if len(idx) == 0:
                st.error("対象データが見つかりませんでした。")
            else:
                ridx = idx[0]
                current = int(df.loc[ridx, "枚数"]) if pd.notna(df.loc[ridx, "枚数"]) else 0
                new_val = current + int(change)

                # 0未満を禁止する場合は以下を有効化
                # if new_val < 0:
                #     st.error("在庫がマイナスになります。値を見直してください。"); st.stop()

                df.loc[ridx, "枚数"] = new_val
                df.loc[ridx, "最終更新日"] = send_date
                save_df(df)
                st.success(f"在庫を {current} → {new_val} に更新しました。")

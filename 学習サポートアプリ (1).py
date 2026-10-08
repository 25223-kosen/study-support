#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date,timedelta
import os

st.set_page_config(page_title="Study Mate",page_icon="📚",layout="wide")
st.title("Study Mate")
st.write("勉強管理アプリ")

st.sidebar.title("メニュー")
st.sidebar.header("ユーザー")
username=st.sidebar.text_input("ニックネームを入力")
if not username:
    st.warning("ニックネームを入力してください")
    st.stop()

data_dir="user_data"
os.makedirs(data_dir,exist_ok=True)
timetable_file=os.path.join(data_dir,f"{username}_timetable.csv")
assignment_file=os.path.join(data_dir,f"{username}_assignments.csv")
test_file=os.path.join(data_dir,f"{username}_tests.csv")

def load_date(file,columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        return pd.DataFrame(columns=columns)

timetable=load_date(timetable_file,["曜日","時限","教科","教室","先生"])
assignments=load_date(assignment_file,["教科","課題名","提出期限","提出済み"])
tests=load_date(test_file,["テスト名","教科","点数","満点","日付"])

menu=st.sidebar.radio("ページを選択",["ホーム","時間割","課題管理","テスト結果","成績分析"])

if menu=="ホーム":
    st.header("ホーム")
    st.subheader("課題")
    if len(assignments)>0:
        unfinished=assignments[assignments["提出済み"].astype(str)!="True"]
        st.write(f"未提出の課題:**{len(unfinished)}件**")
        if len(unfinished)>0:
            for _,row in unfinished.head(5).iterrows():
                try:
                    deadline=pd.to_datetime(row["提出期限"]).date
                    days=(deadline-date.today()).days
                    if days<0:
                        icon="❌"
                        text="期限切れ"
                    elif days<=2:
                        icon="🔴"
                        text=f"あと{days}日"
                    elif days<=6:
                        icon="🟡"
                        text=f"あと{days}日"
                    else:
                        icon="🟢"
                        text=f"あと{days}日"

                    st.write(f"{icon}**{row["教科"]}"
                            f"{row["課題名"]}"
                            f"提出期限：{row["提出期限"]}"
                            f"({text})")

                except:
                    st.write(f"{row["教科"]}:{row["課題名"]}")
    else:
        st.info("課題が入力されていません。")

    st.subheader("テスト記録")
    if len(tests)>0:
        recent_tests=tests.tail(5)
        for _, rou in recent_tests.iterrows():
            try:
                score=float(row["点数"])
                full=float(row["満点"])
                percentage=score/full*100
                st.write(f"{row["教科"]}："
                        f"**{score:.0f}/{full:.0f}点**"
                        f"({percentage:.1f}%)")
            except:
                pass
    else:
        st.info("テスト結果が入力されていません。")

    st.subheader("成績")
    if len(tests)>0:
        tests["点数"]=pd.to_numeric(tests["点数"],errors="coerce")
        average=tests["点数"].mean()
        col1,col2,col3=st.columns(3)
        col1.metric("平均点",f"{average:.1f}点")
        col2.metric("最高点",f"{tests["点数"].max():.0f}点")
        col3.metric("最低点",f"{tests["点数"].min():.0f}点")
    else:
        st.info("テスト結果を入力すると成績が表示されます。")

elif menu=="時間割":
    st.header("時間割")
    st.subheader("時間割を入力")
    with st.form("timetable_form"):
        col1,col2,=st.columns(2)
        with col1:
            day=st.selectbox("曜日",["月","火","水","木","金","土","日"])
            period=st.number_input("時限",min_value=1,max_value=8,value=1,step=1)
            subject=st.text_input("教科")
        with col2:
            classroom=st.text_input("場所")
            teacher=st.text_input("先生")
        submitted=st.form_submit_button("時間割を追加")
        if submitted:
            if subject=="":
                st.error("教科を入力してください。")
            else:
                new_data=pd.DataFrame([{"ニックネーム":username,"曜日":day,"時限":period,"教科":subject,"教室":classroom,"先生":teacher}])
                timetable=pd.concat([timetable,new_data],ignore_index=True)
                timetable.to_csv(timetable_file,index=False,encoding="utf-8-sig")
                st.success("時間割を追加しました。")
                st.rerun()

    st.subheader("登録されている時間割")
    if len(timetable)>0:
        timetable["時限"]=pd.to_numeric(timetable["時限"],errors="coerce")
        timetable=timetable.sort_values(["曜日","時限"])
        st.dataframe(timetable,use_container_width=True)
    else:
        st.info("時間割が入力されていません。")
elif menu=="課題管理":
    st.header("課題管理")
    st.subheader("課題を追加")
    with st.form("assignment_form"):
        col1,col2=st.columns(2)
        with col1:
            subject=st.text_input("教科")
            task=st.text_input("課題名")
        with col2:
            deadline=st.date_input("提出期限",value=date.today())
        submitted=st.form_submit_button("課題を追加")
        if submitted:
            if subject=="" or task=="":
                st.error("教科と課題名を入力してください。")
            else:
                new_data=pd.DataFrame([{"ニックネーム":username,"教科":subject,"課題名":task,"提出期限":deadline.strftime("%Y-%m-%d"),"提出済み":False}])
                assignments=pd.concat([assignments,new_data],ignore_index=True)
                assignments.to_csv(assignment_file,index=False,encoding="utf-8-sig")
                st.success("課題を追加しました。")
                st.rerun()
    st.subheader("課題一覧")
    if len(assignments)>0:
        for index,row in assignments.iterrows():
            try:
                deadline=pd.to_datetime(row["提出期限"]).date()
                days=(deadline-date.today()).days
            except:
                days=999
            if str(["提出済み"])=="True":
                icon="✅"
            elif days<0:
                icon="❌"
            elif days<=2:
                icon="🔴"
            elif days<=6:
                icon="🟡"
            else:
                icon="🟢"
            col1,col2,col3=st.columns([1,5,2])
            with col1:
                st.write(icon)
            with col2:
                st.write(f"**{row["教科"]}**" f"{row["課題名"]}")
                st.write(f"提出期限：{row["提出期限"]}")
            with col3:
                done=st.checkbox("提出済み",value=str(row["提出済み"])=="True",key=f"assignment_{index}")
                if done!=(str(row["提出済み"])=="True"):
                    assignments.loc[index,"提出済み"]=done
                    assignments.to_csv(assignment_file,index=False,encoding="utf-8-sig")
                    st.rerun()
                st.divider()
    else:
        st.info("まだ課題が入力されていません。")

elif menu=="テスト結果":
    st.header("テスト結果")
    st.subheader("テスト結果を追加")
    with st.form("test_form"):
        col1,col2=st.columns(2)
        with col1:
            test_name=st.text_input("テスト名",placeholder="例：1年前期期末")
            subject=st.text_input("教科",placeholder="例：国語")
            score=st.number_input("点数",min_value=0.0,value=0.0,step=1.0)
        with col2:
            full_score=st.number_input("満点",min_value=1.0,value=100.0,step=10.0)
            test_date=st.date_input("テスト日",value=date.today())
        submitted=st.form_submit_button("テスト結果を追加")
        if submitted:
            if test_name=="" or subject=="":
                st.error("テスト名と教科を入力してください。")
            elif score>full_score:
                st.error("点数が満点を超えています")
            else:
                new_data=pd.DataFrame([{"ニックネーム":username,"テスト名":test_name,"教科":subject,"点数":score,"満点":full_score,"日付":test_date.strftime("%Y-%m-%d")}])
                tests=pd.concat([tests,new_data],ignore_index=True)
                tests.to_csv(test_file,index=False,encoding="utf-8-sig")
                st.success("テスト結果を追加しました。")
                st.rerun()
    st.subheader("テスト結果一覧")
    if len(tests)>0:
        display_tests=tests.copy()
        display_tests["点数"]=pd.to_numeric(display_tests["点数"],errors="coerce")
        display_tests["満点"]=pd.to_numeric(display_tests["満点"],errors="coerce")
        display_tests["得点率"]=(display_tests["点数"]/display_tests["満点"]*100).round(1)
        st.dataframe(display_tests,use_container_width=True)
    else:
        st.info("テスト結果が入力されていません")

elif menu=="成績分析":
    st.header("成績分析")
    if len(tests)==0:
        st.info("テスト結果を入力すると、ここで分析できます。")
        st.stop()
    else:
        analysis=tests.copy()
        analysis["点数"]=pd.to_numeric(analysis["点数"],errors="coerce")
        analysis["満点"]=pd.to_numeric(analysis["満点"],errors="coerce")
        analysis["得点率"]=(analysis["点数"]/analysis["満点"]*100)

        average=analysis["点数"].mean()
        max_score=analysis["点数"].max()
        min_score=analysis["点数"].min()
        col1,col2,col3=st.columns(3)
        col1.metric("平均点",f"{average:.1f}点")
        col2.metric("最高点",f"{max_score:.0f}点")
        col3.metric("最低点",f"{min_score:.0f}点")
    st.subheader("教科別平均点")
    subject_ave=(analysis.groupby("教科")["点数"].mean().reset_index())
    subject_ave.columns=["教科","平均点"]
    st.dataframe(subject_ave,use_container_width=True)

    st.subheader("教科別平均")
    fig=px.bar(subject_ave,x="教科",y="平均点",title="教科別平均点")
    st.plotly_chart(fig,use_container_width=True)
    

    st.subheader("点数の推移")
    analysis["日付"]=pd.to_datetime(analysis["日付"],errors="coerce")
    analysis=analysis.sort_values("日付")
    fig2=px.line(analysis,x="日付",y="点数",color="教科",markers=True,title="テストの点数の推移")
    st.plotly_chart(fig2,use_container_width=True)

    st.subheader("教科別分析")
    subjects=analysis["教科"].dropna().unique().tolist()
    selected_sub=st.selectbox("教科を選択",subjects)
    subject_data=analysis[analysis["教科"]==selected_sub]
    if len(subject_data)>0:
        avg=subject_data["点数"].mean()
        st.write(f"**{selected_sub}の平均点："f"{avg:.1f}")
        if len(subject_data)>=2:
            first=subject_data.iloc[0]["点数"]
            latest=subject_data.iloc[-1]["点数"]
            difference=latest-first
            if difference>0:
                st.success(f"前回から{difference:.1f}点上がっています。")
            elif difference<0:
                st.warning(f"前回から{abs(difference):.1f}点下がっています。")
            else:
                st.info("前回と同じ点数です")


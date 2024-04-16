





import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

def image_text(path):

  poster=Image.open(path)
  image_array=np.array(poster)
  reader=easyocr.Reader(["en"])
  text=reader.readtext(image_array,detail=0)

  return text, poster

def extracted_text(text):
  extract={"NAME":[],"ROLE":[],"COMPANY_NAME":[],"CONTACT_NUMBER":[],"EMAIL":[],"WEBSITE":[],"ADDRESS":[],"PINCODE":[]}
  extract["NAME"].append(text[0])
  extract["ROLE"].append(text[1])
  for i in range(2,len(text)):
    if text[i].startswith("+") or (text[i].replace("-","").isdigit() and '-' in text[i]):
      extract["CONTACT_NUMBER"].append(text[i])
    elif "@" in text[i] and ".com" in text[i]:
      extract["EMAIL"].append(text[i])
    elif "WWW" in text[i] or "www" in text[i] or "Www" in text[i] or "wWw" in text[i] or "wwW" in text[i]:
      small=text[i].lower()
      extract["WEBSITE"].append(small)
    elif "Tamil Nadu" in text[i] or "TamilNadu" in text[i] or text[i].isdigit():
      extract["PINCODE"].append(text[i])
    elif re.match(r'^[A-Za-z]',text[i]):
      extract["COMPANY_NAME"].append(text[i])
    else:
      remove_colon=re.sub(r'[,;]','',text[i])
      extract["ADDRESS"].append(remove_colon)
  for key,value in extract.items():
    if len(value)>0:
      concadenate=" ".join(value)
      extract[key]=[concadenate]
    else:
      value="NA"
      extract[key]=[value]
  return extract

# streamlit 

st.set_page_config(layout="wide")
st.title("EXTACTING BUSINESS CARD DATA WITH OCR")
with st.sidebar:
  select=option_menu("MAIN MENU",["HOME","UPLOAD & MODIFY","DELETE"])
if select=="HOME":
  st.header('Welcome to BizCardX')
  home_text = ('This app helps you extract and manage business card details efficiently.')
  st.markdown(f"<h4 text-align: left;'>{home_text} </h4>", unsafe_allow_html=True)
  st.subheader(':orange[About the App:]')
  above_text = ('''BizCardX is a Streamlit web application designed for extracting information 
                from business cards. It utilizes OCR (Optical Character Recognition) to extract 
                text from uploaded images of business cards. The extracted details are then processed 
                and organized into categories such as name, designation, contact information, company 
                name, email, website, address, etc. Users can upload images of business cards, and the app 
                extracts relevant information for storage and management.')
              ''')
                  
  st.markdown(f"<h4 text-align: left;'>{above_text} </h4>", unsafe_allow_html=True)
  st.subheader(":orange[Technologies Used:]")
  tech_text =(''' The app is built using Python and several libraries, including Streamlit for the web 
              interface, EasyOCR for optical character recognition, and SQLAlchemy for database operations. 
              The user interface is designed to be intuitive, allowing users to easily upload business card images, 
              extract details, and manage the stored data. ''')
  st.markdown(f"<h4 text-align: left;'>{tech_text} </h4>", unsafe_allow_html=True)
elif select=="UPLOAD & MODIFY":
  image=st.file_uploader("Upload the Image",type=["png","jpg","jpeg"])
  if image is not None:
    st.image(image,width=300)
    text,poster=image_text(image)
    text_dict=extracted_text(text)
    if text_dict:
      st.success("EXTRACTED")
    df=pd.DataFrame(text_dict)
    image_bytes=io.BytesIO()
    poster.save(image_bytes,format="PNG")
    image_data=image_bytes.getvalue()
    data={"Image":[image_data]}
    df1= pd.DataFrame(data)
    concadenate_df=pd.concat([df,df1],axis=1)
    st.dataframe(concadenate_df)
    button=st.button("Save")
    if button:
      mydb=sqlite3.connect("biscard.db")
      cursor=mydb.cursor()
      #Table creation
      create_table_query='''CREATE TABLE IF NOT EXISTS biscard_details(name varchar(225),
                                                                        role varchar(225),
                                                                        company_name varchar(225),
                                                                        contact_number int,
                                                                        email varchar(225),
                                                                        website varchar(225),
                                                                        address varchar(225),
                                                                        pincode varchar(225),
                                                                        image text)'''

      cursor.execute(create_table_query)
      mydb.commit()
      #INsert query
      insert_query='''INSERT INTO biscard_details(name, role,company_name,contact_number, email, website, address, pincode, image)
                    values(?,?,?,?,?,?,?,?,?)'''

      data=concadenate_df.values.tolist()[0]
      cursor.execute(insert_query,data)
      mydb.commit()
      st.success("SAVED")

  method=st.radio("Select",["Start","Preview","Modify"])
  if method=="Start":
    st.write("")
  if method=="Preview":
    mydb=sqlite3.connect("biscard.db")
    cursor=mydb.cursor()
    select_query="SELECT * from biscard_details"
    cursor.execute(select_query)
    var_table=cursor.fetchall()
    mydb.commit()
    table1=pd.DataFrame(var_table,columns=("NAME","ROLE","COMPANY_NAME","CONTACT_NUMBER","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))
    st.dataframe(table1)


  elif method=="Modify":
    mydb=sqlite3.connect("biscard.db")
    cursor=mydb.cursor()
    select_query="SELECT * from biscard_details"
    cursor.execute(select_query)
    var_table=cursor.fetchall()
    mydb.commit()
    table1=pd.DataFrame(var_table,columns=("NAME","ROLE","COMPANY_NAME","CONTACT_NUMBER","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))
    col1,col2=st.columns(2)
    with col1:
      select_name=st.selectbox("Select the name",table1["NAME"])
    df2=table1[table1["NAME"]==select_name]
    df3=df2.copy() 
     

    col1,col2=st.columns(2)
    with col1:
      modify_name=st.text_input("NAME",df2["NAME"].unique()[0])
      modify_role=st.text_input("ROLE",df2["ROLE"].unique()[0])
      modify_company_name=st.text_input("COMPANY_NAME",df2["COMPANY_NAME"].unique()[0])
      modify_con_num=st.text_input("CONTACT_NUMBER",df2["CONTACT_NUMBER"].unique()[0])
      modify_email=st.text_input("EMAIL",df2["EMAIL"].unique()[0])

      df3["NAME"]=modify_name
      df3["ROLE"]=modify_role
      df3["COMPANY_NAME"]=modify_company_name
      df3["CONTACT_NUMBER"]=modify_con_num
      df3["EMAIL"]=modify_email


    with col2:
      modify_website=st.text_input("WEBSITE",df2["WEBSITE"].unique()[0])
      modify_add=st.text_input("ADDRESS",df2["ADDRESS"].unique()[0])
      modify_pin=st.text_input("PINCODE",df2["PINCODE"].unique()[0])
      modify_img=st.text_input("IMAGE",df2["IMAGE"].unique()[0])
    
      df3["WEBSITE"]=modify_website
      df3["ADDRESS"]=modify_add
      df3["PINCODE"]=modify_pin
      df3["IMAGE"]=modify_img
     
    st.dataframe(df3)

  

    col1,col2=st.columns(2)
    with col1:
      button2=st.button("Modify")
    if button2:
      mydb=sqlite3.connect("biscard.db")
      cursor=mydb.cursor()
      cursor.execute(f"DELETE FROM biscard_details WHERE NAME='{select_name}'")
      mydb.commit()

      insert_query='''INSERT INTO biscard_details(name, role,company_name,contact_number, email, website, address, pincode, image)
                      values(?,?,?,?,?,?,?,?,?)'''
      data=df3.values.tolist()[0]
      cursor.execute(insert_query,data)
      mydb.commit()
      st.success("MODIFIED")     

elif select=="DELETE":
  mydb=sqlite3.connect("biscard.db")
  cursor=mydb.cursor()
  col1,col2=st.columns(2)
  with col1:
    #select query
    select_query="SELECT NAME from biscard_details"
    cursor.execute(select_query)
    var_table2=cursor.fetchall()
    mydb.commit()
    name=[]
    for i in var_table2:
      name.append(i[0])
    name_select=st.selectbox("Select Name",name)



  if name_select:
    col1,col2,col3=st.columns(3)
    with col1:
      st.write(f"Selected Name : {name_select}")
      st.write("") 

      remove=st.button("Delete")
      if remove:
        cursor.execute(f"DELETE FROM biscard_details WHERE NAME ='{name_select}'")
        mydb.commit()

        st.warning("Deleted")

  








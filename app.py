# Import Streamlit and Pandas
import streamlit as st
import pandas as pd
from transformers import pipeline

# Import for API calls
import requests

# Import for navbar
from streamlit_option_menu import option_menu

# Import for dyanmic tagging
from streamlit_tags import st_tags, st_tags_sidebar

# Imports for aggrid
from st_aggrid import AgGrid
from st_aggrid import AgGrid
import pandas as pd
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid import GridUpdateMode, DataReturnMode

# Import for keyboard shortcuts
# from dashboard_utils.gui import keyboard_to_url
# from dashboard_utils.gui import load_keyboard_class

#######################################################

# The code below is to control the layout width of the app.
if "widen" not in st.session_state:
    layout = "centered"
else:
    layout = "wide" if st.session_state.widen else "centered"

#######################################################

# The code below is for the title and logo.
st.set_page_config(layout=layout, page_title="Zero-Shot Text Classification Engine")

#######################################################

# The class below is for adding some formatting to the shortcut button on the left sidebar.
# load_keyboard_class()

#######################################################

# Set up session state so app interactions don't reset the app.
if not "valid_inputs_received" in st.session_state:
    st.session_state["valid_inputs_received"] = False

#######################################################

# The block of code below is to display the title, logos and introduce the app.
st.header("Zero-Shot Text Classification Engine")
st.markdown(
    """
Text Classification engine with No ML training needed

Input any classifying labels (e.g. `Positive`, `Negative` and `Neutral`), or (e.g. `Transactional`, `Informational` and `Navigational`) can
be created for text classification

"""
)

st.sidebar.image("https://cdn.freebiesupply.com/logos/large/2x/tencent-video-logo-png-transparent.png", width=100)
st.sidebar.subheader('About Zero Shot Classification')
st.sidebar.markdown(
    """
Zero-shot classification is a technique that allows us to associate an appropriate label with a piece of text. 
This association is irrespective of the text domain and the aspect

A zero-shot model allows us to classify data that has not been previously used to build the model

"""
)


st.write("")

st.sidebar.subheader("Selection Panel")


#######################################################

# The code below is to display the menu bar.??
with st.sidebar:
    selected = option_menu(
        "",
        ["Demo Mode","Unlocked Mode", "Batch Mode"],
        icons=["bi-key-fill", "bi-key-fill", "bi-key-fill"],
        menu_icon="",
        default_index=0,
    )
st.sidebar.caption("Powered by")
st.sidebar.image('icons.png', width=150)



#######################################################

def main():
    st.caption("")


if selected == "Demo Mode":

    API_KEY = st.secrets["API_KEY"]

    API_URL = (
        "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"
    )

    headers = {"Authorization": f"Bearer {API_KEY}"}

    with st.form(key="my_form"):

        multiselectComponent = st_tags(
            label="",
            text="Add labels - 3 max",
            value=["Transactional", "Informational", "Navigational"],
            suggestions=[
                "Informational",
                "Transactional",
                "Navigational",
                "Positive",
                "Negative",
                "Neutral",
            ],
            maxtags=3,
        )

        new_line = "\n"
        nums = [
            "I want to buy something in this store",
            "How to ask a question about a product",
            "Request a refund through the Google Play store",
            "I have a broken screen, what should I do?",
            "Can I have the link to the product?",
        ]

        sample = f"{new_line.join(map(str, nums))}"

        linesDeduped2 = []

        MAX_LINES = 5
        text = st.text_area(
            "Enter keyphrases to classify (5 phrases max)",
            sample,
            height=200,
            key="2",
            help="At least two keyphrases for the classifier to work, one per line, "
            + str(MAX_LINES)
            + " keyphrases max as part of the demo",
        )
        lines = text.split("\n")  # A list of lines
        linesList = []
        for x in lines:
            linesList.append(x)
        linesList = list(dict.fromkeys(linesList))  # Remove dupes
        linesList = list(filter(None, linesList))  # Remove empty

        if len(linesList) > MAX_LINES:

            st.info(
                f"Only the first "
                + str(MAX_LINES)
                + " keyprases will be reviewed. Unlock that limit by switching to 'Unlocked Mode'"
            )

        linesList = linesList[:MAX_LINES]

        submit_button = st.form_submit_button(label="Submit")

    if not submit_button and not st.session_state.valid_inputs_received:
        st.stop()

    elif submit_button and not text:
        st.warning("There is no keyphrases to classify")
        st.session_state.valid_inputs_received = False
        st.stop()

    elif submit_button and not multiselectComponent:
        st.warning("You have not added any labels, please add some! ")
        st.session_state.valid_inputs_received = False
        st.stop()

    elif submit_button and len(multiselectComponent) == 1:
        st.warning("Please make sure to add at least two labels for classification")
        st.session_state.valid_inputs_received = False
        st.stop()

    elif submit_button or st.session_state.valid_inputs_received:

        if submit_button:
            st.session_state.valid_inputs_received = True

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            # Unhash to check status codes from the API response
            # st.write(response.status_code)
            return response.json()

        listtest = ["I want a refund", "I have a question"]
        listToAppend = []

        for row in linesList:
            output2 = query(
                {
                    "inputs": row,
                    "parameters": {"candidate_labels": multiselectComponent},
                    "options": {"wait_for_model": True},
                }
            )

            listToAppend.append(output2)

            df = pd.DataFrame.from_dict(output2)

        st.success("Done!")

        df = pd.DataFrame.from_dict(listToAppend)

        st.caption("")
        st.markdown("### Check classifier results")
        st.caption("")

        st.checkbox(
            "Widen layout",
            key="widen",
            help="Tick this box to toggle the layout to 'Wide' mode",
        )

        st.caption("")

        # This is a list comprehension to convert the decimals to percentages
        f = [[f"{x:.2%}" for x in row] for row in df["scores"]]

        # This code is for re-integrating the labels back into the dataframe
        df["classification scores"] = f
        df.drop("scores", inplace=True, axis=1)

        # This code is to rename the columns
        df.rename(columns={"sequence": "keyphrase"}, inplace=True)

        # The code below is for Ag-grid

        gb = GridOptionsBuilder.from_dataframe(df)
        # enables pivoting on all columns
        gb.configure_default_column(
            enablePivot=True, enableValue=True, enableRowGroup=True
        )
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        gb.configure_side_bar()
        gridOptions = gb.build()

        response = AgGrid(
            df,
            gridOptions=gridOptions,
            enable_enterprise_modules=True,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            height=300,
            fit_columns_on_grid_load=False,
            configure_side_bar=True,
        )

        # The code below is for the download button

        cs, c1 = st.columns([2, 2])

        with cs:

            @st.cache
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode("utf-8")

            csv = convert_df(df)  #

            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="results.csv",
                mime="text/csv",
            )

elif selected == "Unlocked Mode":

    with st.form(key="my_form"):
        API_KEY2 = st.text_input(
            "Enter HuggingFace API key",
            help="Once you created you HuggiginFace account, you can get your free API token in your settings page: https://huggingface.co/settings/tokens",
        )

        API_URL = (
            "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"
        )

        headers = {"Authorization": f"Bearer {API_KEY2}"}

        multiselectComponent = st_tags(
            label="",
            text="Add labels - 3 max",
            value=["Transactional", "Informational", "Navigational"],
            suggestions=[
                "Informational",
                "Transactional",
                "Navigational",
                "Positive",
                "Negative",
                "Neutral",
            ],
            maxtags=3,
        )

        new_line = "\n"
        nums = [
            "I want to buy something in this store",
            "How to ask a question about a product",
            "Request a refund through the Google Play store",
            "I have a broken screen, what should I do?",
            "Can I have the link to the product?",
        ]

        sample = f"{new_line.join(map(str, nums))}"

        linesDeduped2 = []

        MAX_LINES_FULL = 50
        text = st.text_area(
            "Enter keyphrases to classify",
            sample,
            height=200,
            key="2",
            help="At least two keyphrases for the classifier to work, one per line, "
            + str(MAX_LINES_FULL)
            + " keyphrases max in 'unlocked mode'. You can tweak 'MAX_LINES_FULL' in the code to change this",
        )

        lines = text.split("\n")  # A list of lines
        linesList = []
        for x in lines:
            linesList.append(x)
        linesList = list(dict.fromkeys(linesList))  # Remove dupes from list
        linesList = list(filter(None, linesList))  # Remove empty lines from list

        if len(linesList) > MAX_LINES_FULL:
            st.info(
                f"Note that only the first "
                + str(MAX_LINES_FULL)
                + " keyprases will be reviewed to preserve performance. Fork the repo and tweak 'MAX_LINES_FULL' in the code to increase that limit."
            )

            linesList = linesList[:MAX_LINES_FULL]

        submit_button = st.form_submit_button(label="Submit")

    if not submit_button and not st.session_state.valid_inputs_received:
        st.stop()

    elif submit_button and not text:
        st.warning("There is no keyphrases to classify")
        st.session_state.valid_inputs_received = False
        st.stop()

    elif submit_button and not multiselectComponent:
        st.warning("You have not added any labels, please add some! ")
        st.session_state.valid_inputs_received = False
        st.stop()

    elif submit_button and len(multiselectComponent) == 1:
        st.warning("Please make sure to add at least two labels for classification")
        st.session_state.valid_inputs_received = False
        st.stop()

    elif submit_button or st.session_state.valid_inputs_received:

        try:

            if submit_button:

                st.session_state.valid_inputs_received = True

            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                # Unhash to check status codes from the API response
                # st.write(response.status_code)
                return response.json()

            listtest = ["I want a refund", "I have a question"]
            listToAppend = []

            for row in linesList:
                output2 = query(
                    {
                        "inputs": row,
                        "parameters": {"candidate_labels": multiselectComponent},
                        "options": {"wait_for_model": True},
                    }
                )

                listToAppend.append(output2)

                df = pd.DataFrame.from_dict(output2)

            st.success("Successful")

            df = pd.DataFrame.from_dict(listToAppend)

            st.caption("")
            st.markdown("### Check classification Results")
            st.caption("")

            st.checkbox(
                "Widen layout",
                key="widen",
                help="Tick this box to toggle the layout to 'Wide' mode",
            )

            # This is a list comprehension to convert the decimals to percentages
            f = [[f"{x:.2%}" for x in row] for row in df["scores"]]

            # This code is for re-integrating the labels back into the dataframe
            df["classification scores"] = f
            df.drop("scores", inplace=True, axis=1)

            # This code is to rename the columns
            df.rename(columns={"sequence": "keyphrase"}, inplace=True)

            # The code below is for Ag-grid
            gb = GridOptionsBuilder.from_dataframe(df)
            # enables pivoting on all columns
            gb.configure_default_column(
                enablePivot=True, enableValue=True, enableRowGroup=True
            )
            gb.configure_selection(selection_mode="multiple", use_checkbox=True)
            gb.configure_side_bar()
            gridOptions = gb.build()

            response = AgGrid(
                df,
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                height=300,
                fit_columns_on_grid_load=False,
                configure_side_bar=True,
            )

            # The code below is for the download button

            cs, c1 = st.columns([2, 2])

            with cs:

                @st.cache
                def convert_df(df):
                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                    return df.to_csv().encode("utf-8")

                csv = convert_df(df)  #

                st.caption("")

                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="results.csv",
                    mime="text/csv",
                )

        except ValueError as ve:

            st.warning("Add a valid HuggingFace API key in the text box above")
            st.stop()

elif selected == "Batch Mode":

    st.write('Upload csv file with a single column containing texts for classification')
    st.warning("Kindly contact admin for access")


if __name__ == "__main__":
    main()

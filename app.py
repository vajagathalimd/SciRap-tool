import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import unidecode


# -------------------------------------------------
# TEXT NORMALIZATION
# -------------------------------------------------
def normalize_text(text):
    text = unidecode.unidecode(text)
    text = text.lower()
    text = text.replace("- ", "")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text


# -------------------------------------------------
# REPORTING QUALITY RULES (RQ1–RQ24)
# -------------------------------------------------
RQ_RULES = {
    "RQ1": {"question": "Chemical name or identification was given",
            "strong": ["cas", "chemical name", "cas number", "iupac", "molecular formula", "structure"],
            "weak": ["test compound", "compound", "chemical obtained", "purchased from"]},

    "RQ2": {"question": "Purity was stated or traceable",
            "strong": ["high purity", "certificate of analysis", "hplc", "99%", "batch number", "lot number"],
            "weak": ["purity", "purchased from", "supplied by"]},

    "RQ3": {"question": "Solubility was described",
            "strong": ["solubility", "soluble in", "solubility test"],
            "weak": ["dissolved", "prepared in"]},

    "RQ4": {"question": "Solvent (vehicle) was described",
            "strong": ["dmso", "ethanol", "pbs", "solvent", "vehicle"],
            "weak": ["carrier"]},

    "RQ5": {"question": "Solvent (vehicle) control included",
            "strong": ["vehicle control", "solvent control"],
            "weak": ["control group"]},

    "RQ6": {"question": "Test system described",
            "strong": ["cell line", "primary cells", "tissue", "organ culture", "embryo"],
            "weak": ["cells used", "in vitro model"]},

    "RQ7": {"question": "Source of test system stated",
            "strong": ["atcc", "supplier", "catalog number", "cat no"],
            "weak": ["obtained from", "purchased from"]},

    "RQ8": {"question": "Metabolic competence described",
            "strong": ["cyp450", "s9 fraction", "metabolic activation"],
            "weak": ["metabolize", "biotransformation"]},

    "RQ9": {"question": "Cell passage number stated",
            "strong": ["passage", "p#", "passage number"],
            "weak": ["subcultured"]},

    "RQ10": {"question": "Media composition described",
             "strong": ["dmem", "rpmi", "fbs", "serum", "antibiotic"],
             "weak": ["media", "culture medium"]},

    "RQ11": {"question": "Incubation conditions described",
             "strong": ["37c", "co2", "humidity", "incubator"],
             "weak": ["room temperature"]},

    "RQ12": {"question": "Contamination control described",
             "strong": ["mycoplasma", "contamination check", "sterility test"],
             "weak": ["sterile conditions"]},

    "RQ13": {"question": "Dose levels stated",
             "strong": ["um", "mm", "mg ml", "concentration", "dose"],
             "weak": ["treated with"]},

    "RQ14": {"question": "Cell density or number stated",
             "strong": ["cells well", "seeding density", "cell density"],
             "weak": ["cells plated"]},

    "RQ15": {"question": "Duration of treatment stated",
             "strong": ["24h", "48h", "72h", "exposure time"],
             "weak": ["overnight"]},

    "RQ16": {"question": "Number of replicates stated",
             "strong": ["replicates", "n=", "triplicate", "independent"],
             "weak": ["repeated"]},

    "RQ17": {"question": "Methods sufficiently described",
             "strong": ["protocol", "procedure", "assay method", "analytical method"],
             "weak": ["as previously described"]},

    "RQ18": {"question": "Time points stated",
             "strong": ["time point", "collected at", "measured at"],
             "weak": ["over time"]},

    "RQ19": {"question": "Cytotoxicity measured",
             "strong": ["mtt", "viability", "cytotoxicity", "ldh"],
             "weak": ["cell death"]},

    "RQ20": {"question": "Results clearly presented",
             "strong": ["figure", "table", "results"],
             "weak": ["data shown"]},

    "RQ21": {"question": "Statistical methods described",
             "strong": ["anova", "t test", "p value", "graphpad"],
             "weak": ["statistics"]},

    "RQ22": {"question": "Funding sources stated",
             "strong": ["funded by", "supported by", "grant"],
             "weak": ["financial support"]},

    "RQ23": {"question": "Competing interests disclosed",
             "strong": [
                 "no conflict of interest",
                 "no conflicts of interest",
                 "the authors declare no conflict",
                 "the authors declare that they have no conflict of interest",
                 "no competing interests",
                 "none declared",
                 "no financial conflict",
                 "no competing financial interests"
             ],
             "weak": ["conflict of interest", "competing interest"]},

    "RQ24": {"question": "Indispensable information provided",
             "strong": [], "weak": []}
}


# -------------------------------------------------
# METHOD QUALITY RULES (MQ1–MQ16)
# -------------------------------------------------
MQ_RULES = {
    "MQ1": {"question": "Impurities unlikely to affect results",
            "strong": ["high purity", "hplc", "99%", "no impurities"],
            "weak": ["purity", "batch", "lot number"],
            "contradict": ["impurities", "unknown purity"]},

    "MQ2": {"question": "Compound likely soluble",
            "strong": ["soluble", "solubility", "fully dissolved"],
            "weak": ["dissolved"],
            "contradict": ["insoluble", "precipitate"]},

    "MQ3": {"question": "Appropriate solvent used",
            "strong": ["dmso", "ethanol", "pbs"],
            "weak": ["solvent"],
            "contradict": ["toxic solvent"]},

    "MQ4": {"question": "Solvent control included",
            "strong": ["vehicle control", "solvent control"],
            "weak": ["control group"],
            "contradict": ["no control"]},

    "MQ5": {"question": "Positive control included + expected effect",
            "strong": ["positive control", "reference compound", "expected response"],
            "weak": ["positive"],
            "contradict": ["no positive control", "failed positive control"]},

    "MQ6": {"question": "Reliable + sensitive test system",
            "strong": ["validated model", "sensitive assay", "cyp450"],
            "weak": ["cell line", "primary cells"],
            "contradict": ["unreliable"]},

    "MQ7": {"question": "Maintenance conditions appropriate",
            "strong": ["37c", "co2", "dmem", "fbs", "mycoplasma free"],
            "weak": ["incubation", "media"],
            "contradict": ["contamination"]},

    "MQ8": {"question": "Exposure duration suitable",
            "strong": ["24h", "48h", "72h"],
            "weak": ["treated for"],
            "contradict": ["insufficient exposure"]},

    "MQ9": {"question": "Concentrations suitable",
            "strong": ["dose response", "range finding", "multiple concentrations"],
            "weak": ["treated with"],
            "contradict": ["irrelevant concentration", "excessive toxicity"]},

    "MQ10": {"question": "Test conditions appropriate",
             "strong": ["appropriate media", "serum", "cell density", "temperature"],
             "weak": ["culture"],
             "contradict": ["inappropriate conditions"]},

    "MQ11": {"question": "Reliable analytical methods used",
             "strong": ["validated method", "sensitivity", "lod", "standard method"],
             "weak": ["method", "protocol"],
             "contradict": ["unvalidated"]},

    "MQ12": {"question": "Sufficient replicates",
             "strong": ["n=", "triplicate", "biological replicates"],
             "weak": ["replicated"],
             "contradict": ["n=1", "single replicate"]},

    "MQ13": {"question": "Suitable time points",
             "strong": ["time course", "measured at", "multiple time points"],
             "weak": ["over time"],
             "contradict": ["inadequate time points"]},

    "MQ14": {"question": "Cytotoxicity measured & acceptable",
             "strong": ["mtt", "viability", "cytotoxicity", "noncytotoxic"],
             "weak": ["cell death"],
             "contradict": ["severe cytotoxicity"]},

    "MQ15": {"question": "Statistical methods appropriate",
             "strong": ["anova", "t test", "p value"],
             "weak": ["statistics"],
             "contradict": ["inappropriate statistics"]},

    "MQ16": {"question": "Other reliability factors",
             "strong": ["quality control", "validated"],
             "weak": ["reliable"],
             "contradict": ["bias", "experimental flaw"]}
}


# -------------------------------------------------
# RELEVANCE RULES (R1–R4)
# -------------------------------------------------
R_RULES = {
    "R1": {
        "question": "Identity of the tested substance",
        "direct": [
            "pesticide", "insecticide", "herbicide", "fungicide",
            "endocrine disruptor", "bisphenol", "phthalate", "flame retardant",
            "metal", "lead", "arsenic", "cadmium", "mercury"
        ],
        "indirect": [
            "industrial chemical", "environmental toxicant", "pollution exposure"
        ],
        "not_rel": [
            "pharmaceutical drug", "antidepressant", "vitamin",
            "nutraceutical", "nanomaterial", "hormone therapy", "food additive"
        ]
    },

    "R2": {
        "question": "Test system used",
        "direct": [
            "oligodendrocyte", "opc", "myelination", "cns development",
            "prenatal", "perinatal", "early life", "white matter",
            "developmental neurotoxicity"
        ],
        "indirect": ["neuron culture", "mixed glia", "primary brain cells"],
        "not_rel": [
            "cancer cell line", "glioblastoma", "hepg2", "a549",
            "alzheimer", "parkinson", "ms", "adult neurodegeneration"
        ]
    },

    "R3": {
        "question": "Endpoint studied",
        "direct": [
            "myelin", "mbp", "olig2", "apoptosis", "oxidative stress",
            "mitochondrial dysfunction", "ros", "cytokine",
            "inflammation", "neurite outgrowth", "cell differentiation",
            "developmental toxicity"
        ],
        "indirect": ["neurotoxicity", "viability", "cytotoxicity", "gene expression"],
        "not_rel": [
            "cancer proliferation", "tumor marker",
            "alzheimer marker", "parkinson marker", "metabolic disease"
        ]
    },

    "R4": {
        "question": "Concentrations used",
        "direct": ["nm", "µm", "low dose", "physiological dose"],
        "indirect": ["high µm", "supraphysiological dose"],
        "not_rel": ["mm", "millimolar", "extremely high dose", "cytotoxic concentration"]
    }
}


# -------------------------------------------------
# PDF EXTRACTION
# -------------------------------------------------
def extract_pdf_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "".join(page.get_text() for page in doc)
    return normalize_text(text)


# -------------------------------------------------
# SCORING ENGINE (RQ + MQ)
# -------------------------------------------------
def evaluate_rule(strong, weak, contradict, text):
    s_hits = [k for k in strong if k in text]
    w_hits = [k for k in weak if k in text]
    c_hits = [k for k in contradict if k in text]

    if c_hits:
        return "Not fulfilled", f"Contradictory: {', '.join(c_hits)}"
    if s_hits:
        return "Fulfilled", f"Strong: {', '.join(s_hits)}"
    if w_hits:
        return "Partially fulfilled", f"Weak: {', '.join(w_hits)}"
    return "Not reported", "No information found."


# -------------------------------------------------
# RELEVANCE ENGINE (R1–R4)
# -------------------------------------------------
def evaluate_relevance(direct, indirect, not_rel, text):
    d_hits = [k for k in direct if k in text]
    i_hits = [k for k in indirect if k in text]
    n_hits = [k for k in not_rel if k in text]

    if n_hits:
        return "Not relevant", f"Excluded terms: {', '.join(n_hits)}"
    if d_hits:
        return "Directly relevant", f"Direct: {', '.join(d_hits)}"
    if i_hits:
        return "Indirectly relevant", f"Indirect: {', '.join(i_hits)}"
    return "Not relevant", "No relevance terms found."


# -------------------------------------------------
# NUMERIC SCORE MAPPING
# -------------------------------------------------
RQ_SCORES = {"Fulfilled": 1, "Partially fulfilled": 0.5, "Not fulfilled": 0}
MQ_SCORES = {"Fulfilled": 1, "Partially fulfilled": 0.5, "Not fulfilled": 0, "Not reported": 0}
REL_SCORES = {"Directly relevant": 1, "Indirectly relevant": 0.5, "Not relevant": 0}


# -------------------------------------------------
# COLOR FUNCTIONS
# -------------------------------------------------
def color_rq(val):
    return {
        "Fulfilled": "background-color: green; color: white;",
        "Partially fulfilled": "background-color: yellow; color: black;",
        "Not fulfilled": "background-color: red; color: white;"
    }.get(val, "")


def color_mq(val):
    return {
        "Fulfilled": "background-color: green; color: white;",
        "Partially fulfilled": "background-color: yellow; color: black;",
        "Not fulfilled": "background-color: red; color: white;",
        "Not reported": "background-color: lightgray; color: black;"
    }.get(val, "")


def color_rel(val):
    return {
        "Directly relevant": "background-color: green; color: white;",
        "Indirectly relevant": "background-color: yellow; color: black;",
        "Not relevant": "background-color: red; color: white;"
    }.get(val, "")


# -------------------------------------------------
# STREAMLIT APP
# -------------------------------------------------
st.title("🧪 Complete SciRAP In Vitro Evaluation Tool")
st.write("Includes Reporting Quality, Methodological Quality, Relevance, and Scoring.")

uploaded_pdf = st.file_uploader("📄 Upload PDF", type=["pdf"], key="upload_pdf")

if uploaded_pdf:

    text = extract_pdf_text(uploaded_pdf)
    st.success("PDF processed successfully!")

    # -------------------------------------------------
    # RQ EVALUATION
    # -------------------------------------------------
    st.header("📘 REPORTING QUALITY (RQ1–RQ24)")
    rq_out = []

    for rq, rule in RQ_RULES.items():
        score, expl = evaluate_rule(rule["strong"], rule["weak"], [], text)
        rq_out.append([rq, rule["question"], score, expl])

    rq_df = pd.DataFrame(rq_out, columns=["RQ", "Question", "Score", "Explanation"])
    rq_df["Numeric Score"] = rq_df["Score"].map(RQ_SCORES)
    rq_total = rq_df["Numeric Score"].sum()

    st.dataframe(rq_df.style.applymap(color_rq, subset=["Score"]), use_container_width=True)
    st.subheader(f"RQ Total Score = {rq_total} / {len(rq_df)}")

    # -------------------------------------------------
    # MQ EVALUATION
    # -------------------------------------------------
    st.header("🔬 METHODOLOGICAL QUALITY (MQ1–MQ16)")
    mq_out = []

    for mq, rule in MQ_RULES.items():
        score, expl = evaluate_rule(rule["strong"], rule["weak"], rule["contradict"], text)
        mq_out.append([mq, rule["question"], score, expl])

    mq_df = pd.DataFrame(mq_out, columns=["MQ", "Question", "Score", "Explanation"])
    mq_df["Numeric Score"] = mq_df["Score"].map(MQ_SCORES)
    mq_total = mq_df["Numeric Score"].sum()

    st.dataframe(mq_df.style.applymap(color_mq, subset=["Score"]), use_container_width=True)
    st.subheader(f"MQ Total Score = {mq_total} / {len(mq_df)}")

    # -------------------------------------------------
    # RELEVANCE EVALUATION
    # -------------------------------------------------
    st.header("🎯 RELEVANCE (R1–R4)")
    rel_out = []

    for r, rule in R_RULES.items():
        score, expl = evaluate_relevance(rule["direct"], rule["indirect"], rule["not_rel"], text)
        rel_out.append([r, rule["question"], score, expl])

    rel_df = pd.DataFrame(rel_out, columns=["R", "Question", "Score", "Explanation"])
    rel_df["Numeric Score"] = rel_df["Score"].map(REL_SCORES)
    rel_total = rel_df["Numeric Score"].sum()

    st.dataframe(rel_df.style.applymap(color_rel, subset=["Score"]), use_container_width=True)
    st.subheader(f"Relevance Total Score = {rel_total} / {len(rel_df)}")

    # -------------------------------------------------
    # FINAL COMBINED SCORE
    # -------------------------------------------------
    st.header("🏁 FINAL STUDY SCORE SUMMARY")

    final_score = rq_total + mq_total + rel_total
    max_score = len(rq_df) + len(mq_df) + len(rel_df)

    st.subheader(f"### ✔ Final Score: **{final_score} / {max_score}**")

    if final_score >= 0.75 * max_score:
        st.success("Overall Quality: HIGH")
    elif final_score >= 0.50 * max_score:
        st.warning("Overall Quality: MODERATE")
    else:
        st.error("Overall Quality: LOW")

    # -------------------------------------------------
    # DOWNLOAD BUTTONS
    # -------------------------------------------------
    st.subheader("⬇ Download Results")

    st.download_button("Download RQ CSV",
                       rq_df.to_csv(index=False),
                       file_name="RQ_results.csv")

    st.download_button("Download MQ CSV",
                       mq_df.to_csv(index=False),
                       file_name="MQ_results.csv")

    st.download_button("Download Relevance CSV",
                       rel_df.to_csv(index=False),
                       file_name="Relevance_results.csv")

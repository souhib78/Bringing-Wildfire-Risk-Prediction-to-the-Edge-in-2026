const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, ImageRun,
  BorderStyle, PageNumber, Footer, Header
} = require("docx");
const fs = require("fs");

const FEAT_IMG = fs.readFileSync("../outputs/feature_importance.png");
const CM_IMG = fs.readFileSync("../outputs/confusion_matrix.png");
const ROC_IMG = fs.readFileSync("../outputs/roc_curve.png");

// ---------- helpers ----------
function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } });
}
function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 160 },
    alignment: AlignmentType.JUSTIFIED,
  });
}
function pRuns(runs, opts = {}) {
  return new Paragraph({ children: runs, spacing: { after: 160 }, alignment: AlignmentType.JUSTIFIED, ...opts });
}
function bold(text) { return new TextRun({ text, bold: true }); }
function italic(text) { return new TextRun({ text, italics: true }); }
function normal(text) { return new TextRun({ text }); }

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "D9534F" } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text, bold: !!opts.header, color: opts.header ? "FFFFFF" : "000000", size: opts.size || 20 })],
      alignment: opts.align || AlignmentType.LEFT,
    })],
    verticalAlign: "center",
  });
}

function refItem(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 20 })],
    spacing: { after: 120 },
    indent: { left: 360, hanging: 360 },
  });
}

function figure(imgBuffer, widthPx, heightPx, caption) {
  const maxWidthEMU = 5.5; // inches
  const ratio = heightPx / widthPx;
  const widthIn = Math.min(5.5, maxWidthEMU);
  const heightIn = widthIn * ratio;
  return [
    new Paragraph({
      children: [new ImageRun({ data: imgBuffer, type: "png", transformation: { width: widthIn * 96, height: heightIn * 96 } })],
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, after: 80 },
    }),
    new Paragraph({
      children: [new TextRun({ text: caption, italics: true, size: 19 })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),
  ];
}

// ---------- document ----------
const doc = new Document({
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } },
    },
    headers: {
      default: new Header({ children: [new Paragraph({ children: [new TextRun({ text: "Machine Learning-Based Wildfire Prediction — Algeria Case Study", size: 16, italics: true })], alignment: AlignmentType.CENTER })] }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], size: 18 })],
        })],
      }),
    },
    children: [
      // Title
      new Paragraph({
        children: [new TextRun({
          text: "Machine Learning-Based Wildfire Occurrence Prediction Using Meteorological and Fire Weather Index Data: A Case Study from Algeria",
          bold: true, size: 32,
        })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "[Author Name]¹, [Co-Author Name]²", size: 22 })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "¹[Department, University, City, Algeria]   ²[Department, University, City, Country]", size: 18, italics: true })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 60 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "[corresponding.email@example.com]", size: 18, italics: true })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 300 },
      }),

      // Abstract
      pRuns([bold("Abstract — ")].concat([normal(
        "Wildfires pose a growing threat to ecosystems, property, and human life in the Mediterranean Maghreb, as illustrated by the severe 2021 and 2022 fire seasons in northern Algeria. While machine learning-based wildfire prediction has been studied extensively in Europe and North America, the Maghreb region remains comparatively underexplored. This paper presents a fully reproducible machine learning pipeline for predicting daily wildfire occurrence in Algeria using meteorological observations and Fire Weather Index (FWI) system components. Using the public Algerian Forest Fires Dataset (244 daily records from the Bejaia and Sidi Bel-Abbes regions, summer 2012), we train and compare a Random Forest classifier against a Logistic Regression baseline. The Random Forest model achieves 98.0% test accuracy (F1 = 0.982, ROC-AUC = 1.000), confirmed by 5-fold cross-validation (98.4% ± 2.4%), and identifies the Initial Spread Index (ISI) and Fine Fuel Moisture Code (FFMC) as the dominant predictors. We discuss this result critically, noting that part of the apparent separability stems from the analytical relationship between FWI sub-indices and the underlying weather variables, and we situate our results against prior studies on the same dataset. All code, data processing scripts, and a one-click Google Colab notebook are released publicly to support reproducibility and future extensions, including multi-region and multi-modal (satellite imagery) wildfire prediction for Algeria."
      )])),
      pRuns([bold("Keywords: "), italic("wildfire prediction; machine learning; random forest; Fire Weather Index; Algeria; reproducibility")]),

      // 1. Introduction
      h1("1. Introduction"),
      p("Forest fires are among the most destructive natural hazards affecting Mediterranean ecosystems, causing loss of life, biodiversity, and economic damage every year. Algeria has experienced particularly severe wildfire seasons in recent years: the August 2021 fires in Kabylie alone burned tens of thousands of hectares and resulted in significant loss of life, drawing national and international attention to the country's wildfire preparedness. Meteorological conditions — temperature, humidity, wind, and antecedent drought — are well established drivers of fire ignition and spread, and are formalized in fire-danger rating systems such as the Canadian Fire Weather Index (FWI) system."),
      p("Machine learning (ML) offers a data-driven complement to traditional fire-danger indices, learning nonlinear relationships between weather conditions and observed fire occurrence directly from historical records. Such models have been widely studied for Mediterranean Europe, where dense meteorological networks and long historical fire records are available. In contrast, ML-based wildfire studies specific to Algeria and the broader Maghreb remain comparatively scarce, despite the region's high fire risk and shared Mediterranean fire regime with southern Europe."),
      p("This paper makes three contributions. First, we build and rigorously evaluate a Random Forest classifier for daily wildfire occurrence prediction using the public Algerian Forest Fires Dataset, comparing it against a Logistic Regression baseline and against results reported in prior studies on the same data. Second, we provide a transparent, critical discussion of an important pitfall in this dataset — the near-perfect separability achievable by some FWI sub-indices, which partly reflects their analytical derivation from the raw weather variables rather than purely learned predictive signal. Third, we release a fully reproducible, open-source pipeline, including a one-click Google Colab notebook, to lower the barrier for other researchers and students working on Algerian and Maghreb wildfire data, and we outline a concrete path toward multi-region and multi-modal extensions."),

      // 2. Related Work
      h1("2. Related Work"),
      p("Data-driven wildfire prediction has a long history in the machine learning literature. Cortez and Morais (2007) pioneered the use of meteorological data mining to predict burned area in Portugal's Montesinho Natural Park, comparing several algorithms including Support Vector Machines and Random Forests on a dataset that later became a standard benchmark in the field."),
      p("For Algeria specifically, Abid and Izeboudjen (2020) introduced the Algerian Forest Fires Dataset used in this study, proposing a decision-tree-based system intended for embedded smart-sensor deployment and reporting 82.92% classification accuracy. Zaidi (2023) later applied an artificial neural network with PCA-based dimensionality reduction (6 components, 96.65% variance retained) to the same dataset, comparing against Logistic Regression, k-Nearest Neighbors, SVM, and Random Forest baselines under 10-fold stratified cross-validation, and reported an accuracy of 96.7% ± 2.6% (F1 = 0.971 ± 0.023) for the ANN, with SHAP analysis highlighting RH, DC, and ISI as influential features. More recently, a CNN-BiLSTM hybrid deep learning model evaluated on the same 244-record dataset reported accuracy as high as 99.99% with a near-perfect ROC-AUC, and a separate study comparing Random Forest and Boosting classifiers on time and environmental factors reported 89.6% accuracy for Boosting and an AUC of 0.978 for Random Forest."),
      p("Table 1 situates the present work against this prior literature on the same dataset. Notably, accuracy figures across studies cluster very close to the ceiling (83–100%), which — combined with the small sample size (244 records) — suggests that the dataset itself is close to linearly/near-linearly separable given the FWI features, a point we return to in Section 6."),

      // Table 1: related work comparison
      new Table({
        width: { size: 9350, type: WidthType.DXA },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              cell("Study", { header: true, width: 2400 }),
              cell("Method", { header: true, width: 2600 }),
              cell("Accuracy", { header: true, width: 1500, align: AlignmentType.CENTER }),
              cell("F1 / AUC", { header: true, width: 1500, align: AlignmentType.CENTER }),
              cell("Notes", { header: true, width: 1350 }),
            ],
          }),
          new TableRow({ children: [
            cell("Abid & Izeboudjen (2020)", { width: 2400 }),
            cell("Decision Tree", { width: 2600 }),
            cell("82.9%", { width: 1500, align: AlignmentType.CENTER }),
            cell("—", { width: 1500, align: AlignmentType.CENTER }),
            cell("Original dataset paper", { width: 1350 }),
          ]}),
          new TableRow({ children: [
            cell("RF vs. Boosting study (2025)", { width: 2400 }),
            cell("Boosting / Random Forest", { width: 2600 }),
            cell("89.6%", { width: 1500, align: AlignmentType.CENTER }),
            cell("AUC 0.978 (RF)", { width: 1500, align: AlignmentType.CENTER }),
            cell("Time + weather features", { width: 1350 }),
          ]}),
          new TableRow({ children: [
            cell("Zaidi (2023)", { width: 2400 }),
            cell("ANN + PCA (6 comp.)", { width: 2600 }),
            cell("96.7% ± 2.6%", { width: 1500, align: AlignmentType.CENTER }),
            cell("F1 0.971 ± 0.023", { width: 1500, align: AlignmentType.CENTER }),
            cell("10-fold CV, SHAP analysis", { width: 1350 }),
          ]}),
          new TableRow({ children: [
            cell("CNN-BiLSTM study (2025)", { width: 2400 }),
            cell("CNN + BiLSTM", { width: 2600 }),
            cell("99.99%", { width: 1500, align: AlignmentType.CENTER }),
            cell("AUC ≈ 1.00", { width: 1500, align: AlignmentType.CENTER }),
            cell("Deep learning, small data", { width: 1350 }),
          ]}),
          new TableRow({ children: [
            cell("This work", { width: 2400, header: false }),
            cell("Random Forest (+ LR baseline)", { width: 2600 }),
            cell("98.0%", { width: 1500, align: AlignmentType.CENTER }),
            cell("F1 0.982 / AUC 1.000", { width: 1500, align: AlignmentType.CENTER }),
            cell("Full feature set, 5-fold CV, open-source + Colab", { width: 1350 }),
          ]}),
        ],
      }),
      new Paragraph({ children: [new TextRun({ text: "Table 1. Comparison with prior studies using the Algerian Forest Fires Dataset.", italics: true, size: 19 })], alignment: AlignmentType.CENTER, spacing: { before: 100, after: 300 } }),

      // 3. Data and Study Area
      h1("3. Data and Study Area"),
      p("We use the publicly available Algerian Forest Fires Dataset (UCI Machine Learning Repository), comprising 244 daily observations collected during the June–September 2012 fire season across two regions: Bejaia (northeastern Algeria) and Sidi Bel-Abbes (northwestern Algeria). Each record includes standard meteorological variables (temperature, relative humidity, wind speed, rainfall) and five components of the Canadian Fire Weather Index system (FFMC, DMC, DC, ISI, BUI), along with a binary fire/no-fire label. The dataset contains 138 fire days and 106 non-fire days, a mild class imbalance addressed via stratified sampling in our evaluation."),
      p("The raw CSV file combines both regions in a single file with two stacked header blocks and contains a documented formatting artifact — a missing field delimiter in one record — which we detect and repair programmatically as part of an automated, auditable preprocessing step (see accompanying code repository)."),

      // 4. Methodology
      h1("4. Methodology"),
      h2("4.1 Feature Set"),
      p("We use nine input features: Temperature, Relative Humidity (RH), Wind speed (Ws), Rainfall, and the five FWI sub-indices (FFMC, DMC, DC, ISI, BUI). The final composite FWI score itself is excluded from the input feature set, since it is deterministically computed from ISI and BUI and its inclusion would constitute direct target leakage."),
      h2("4.2 Models"),
      p("We train a Random Forest classifier (200 trees, maximum depth 6, scikit-learn implementation) as our primary model, and a Logistic Regression classifier (with standardized features) as an interpretable linear baseline. Both models are trained on an 80/20 stratified train-test split (random state fixed for reproducibility)."),
      h2("4.3 Evaluation"),
      p("We report accuracy, precision, recall, F1-score, and ROC-AUC on the held-out test set. To assess the stability of the Random Forest result beyond a single train-test split, we additionally report 5-fold stratified cross-validation accuracy on the full dataset."),

      // 5. Results
      h1("5. Results"),
      p("Table 2 summarizes test-set performance for both models. The Random Forest classifier outperforms the Logistic Regression baseline across all metrics and achieves near-perfect separation on the held-out test set."),

      new Table({
        width: { size: 9350, type: WidthType.DXA },
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("Model", { header: true, width: 2600 }),
            cell("Accuracy", { header: true, width: 1700, align: AlignmentType.CENTER }),
            cell("Precision", { header: true, width: 1700, align: AlignmentType.CENTER }),
            cell("Recall", { header: true, width: 1700, align: AlignmentType.CENTER }),
            cell("F1", { header: true, width: 1650, align: AlignmentType.CENTER }),
            cell("ROC-AUC", { header: true, width: 1700, align: AlignmentType.CENTER }),
          ]}),
          new TableRow({ children: [
            cell("Random Forest", { width: 2600 }),
            cell("0.980", { width: 1700, align: AlignmentType.CENTER }),
            cell("0.966", { width: 1700, align: AlignmentType.CENTER }),
            cell("1.000", { width: 1700, align: AlignmentType.CENTER }),
            cell("0.982", { width: 1650, align: AlignmentType.CENTER }),
            cell("1.000", { width: 1700, align: AlignmentType.CENTER }),
          ]}),
          new TableRow({ children: [
            cell("Logistic Regression", { width: 2600 }),
            cell("0.939", { width: 1700, align: AlignmentType.CENTER }),
            cell("0.931", { width: 1700, align: AlignmentType.CENTER }),
            cell("0.964", { width: 1700, align: AlignmentType.CENTER }),
            cell("0.947", { width: 1650, align: AlignmentType.CENTER }),
            cell("0.988", { width: 1700, align: AlignmentType.CENTER }),
          ]}),
        ],
      }),
      new Paragraph({ children: [new TextRun({ text: "Table 2. Test-set performance (20% held-out split, n = 49).", italics: true, size: 19 })], alignment: AlignmentType.CENTER, spacing: { before: 100, after: 240 } }),
      p("5-fold stratified cross-validation on the full dataset confirms the Random Forest result is stable rather than an artifact of a favorable split: mean accuracy 98.4% (± 2.4% standard deviation across folds)."),

      ...figure(FEAT_IMG, 1200, 750, "Figure 1. Random Forest feature importance. ISI and FFMC jointly account for 71% of total importance."),
      ...figure(CM_IMG, 750, 600, "Figure 2. Confusion matrix on the held-out test set (n = 49): 1 false positive, 0 false negatives."),
      ...figure(ROC_IMG, 900, 750, "Figure 3. ROC curve for the Random Forest classifier (AUC = 1.000)."),

      p("Feature importance analysis (Figure 1) shows that ISI (Initial Spread Index) and FFMC (Fine Fuel Moisture Code) together account for approximately 71% of total predictive importance, consistent with fire science: both indices directly encode fuel flammability and expected fire spread rate, and are therefore mechanistically close to the fire/no-fire outcome."),

      // 6. Discussion and Limitations
      h1("6. Discussion and Limitations"),
      p("Our results are competitive with, and in several respects exceed, prior work on the same dataset (Table 1) while using a comparatively simple, interpretable model. However, several limitations temper this conclusion and are important for honest scientific reporting."),
      pRuns([bold("Sample size and single-season scope. "), normal("With only 244 records from a single fire season (2012) in two regions, all models evaluated on this dataset — including this study — operate on a small held-out test set (n = 49 here), inflating the variance of point-estimate metrics and the risk of optimistic results from a favorable split. Our 5-fold cross-validation partially mitigates, but does not eliminate, this concern.")]),
      pRuns([bold("Structural leakage within the FWI system. "), normal("The near-perfect ROC-AUC (1.000) should not be over-interpreted as evidence that wildfire occurrence is a trivially solved problem. ISI and FFMC are themselves analytically derived from temperature, relative humidity, and wind speed via the Canadian FWI system's published formulas. This means part of the apparent predictive power reflects the fact that FWI designers already engineered these indices to track fire danger closely, rather than the Random Forest discovering a novel relationship from raw weather data alone. This caveat likely also explains why multiple independent studies on this same dataset (Table 1) report unusually high accuracy regardless of model family.")]),
      pRuns([bold("Generalization. "), normal("The dataset covers only two regions and one year; performance on other Algerian wilayas, other years, or under climate-change-shifted fire regimes is untested and should not be assumed.")]),
      p("We view these limitations not as weaknesses to conceal but as the primary motivation for the future work outlined below: larger, multi-year, multi-region data collection, and multi-modal architectures that are less dependent on any single engineered index family."),

      // 7. Conclusion and Future Work
      h1("7. Conclusion and Future Work"),
      p("We presented a reproducible machine learning pipeline for wildfire occurrence prediction in Algeria, achieving 98.0% test accuracy with a Random Forest classifier on the Algerian Forest Fires Dataset, and situated this result critically against five prior studies on the same data. All code, a cleaned dataset, trained-model evaluation scripts, and a one-click Google Colab notebook are released publicly to support reproducibility."),
      p("Future work will extend this pipeline along three directions: (i) incorporating multi-year and multi-region Algerian data as it becomes available, to test temporal and spatial generalization; (ii) fusing meteorological data with satellite imagery (e.g., Sentinel-2/MODIS vegetation and moisture indices) in a multi-modal architecture; and (iii) exploring domain adaptation techniques to transfer knowledge from data-rich European Mediterranean wildfire datasets to data-scarce Algerian and Maghreb contexts — a direction motivated by the shared Mediterranean fire regime but distinct data availability between the two regions."),

      // Data and Code Availability
      h1("Data and Code Availability"),
      pRuns([normal("The dataset is publicly available from the UCI Machine Learning Repository. All preprocessing code, model training scripts, figures, and a one-click Google Colab notebook reproducing every result in this paper are available at: "), italic("https://github.com/Machine-Learning-Based-Wildfire/Machine-Learning-pipeline-predicts-daily-wildfires-in-Algeria"), normal(".")]),

      // References
      h1("References"),
      refItem("Abid, F., & Izeboudjen, N. (2020). Predicting forest fire in Algeria using data mining techniques: Case study of the decision tree algorithm. In M. Ezziyyani (Ed.), Advanced Intelligent Systems for Sustainable Development (AI2SD'2019), Advances in Intelligent Systems and Computing, vol. 1105 (pp. 363–370). Springer, Cham. https://doi.org/10.1007/978-3-030-36674-2_37"),
      refItem("Abid, F. (2019). Algerian Forest Fires [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5KW4N"),
      refItem("Cortez, P., & Morais, A. (2007). A data mining approach to predict forest fires using meteorological data. In J. Neves, M. F. Santos, & J. Machado (Eds.), New Trends in Artificial Intelligence, Proceedings of the 13th EPIA 2007 (pp. 512–523). Guimarães, Portugal."),
      refItem("Zaidi, A. (2023). Predicting wildfires in Algerian forests using machine learning models. Heliyon / PMC. Retrieved from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10372657/"),
      refItem("Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32."),
      refItem("Van Wagner, C. E. (1987). Development and structure of the Canadian Forest Fire Weather Index System. Canadian Forestry Service, Forestry Technical Report 35."),
      refItem("Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830."),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("wildfire_paper.docx", buffer);
  console.log("Paper generated: wildfire_paper.docx");
});

// ===================================================================
// Algerian Wildfire Risk — Embedded Random Forest Model
// Auto-generated from a scikit-learn RandomForestClassifier.
// 10 trees, max_depth=4, 9 input features.
// Feature order: Temperature, RH, Ws, Rain, FFMC, DMC, DC, ISI, BUI
// ===================================================================
#ifndef WILDFIRE_MODEL_H
#define WILDFIRE_MODEL_H

#define N_FEATURES 9
#define N_TREES 10

float tree_0(float *x) {
    if (x[3] <= 0.0500f) {
        if (x[8] <= 7.4000f) {
            return 0.000000f;
        } else {
            if (x[4] <= 82.1500f) {
                if (x[2] <= 13.0000f) {
                    return 0.000000f;
                } else {
                    return 0.500000f;
                }
            } else {
                return 1.000000f;
            }
        }
    } else {
        if (x[1] <= 45.5000f) {
            return 1.000000f;
        } else {
            if (x[5] <= 8.1500f) {
                return 0.000000f;
            } else {
                if (x[6] <= 20.5000f) {
                    return 0.000000f;
                } else {
                    return 0.444444f;
                }
            }
        }
    }
}

float tree_1(float *x) {
    if (x[7] <= 2.5500f) {
        return 0.000000f;
    } else {
        if (x[1] <= 75.5000f) {
            return 1.000000f;
        } else {
            if (x[0] <= 32.5000f) {
                return 1.000000f;
            } else {
                if (x[8] <= 21.9000f) {
                    return 0.000000f;
                } else {
                    return 1.000000f;
                }
            }
        }
    }
}

float tree_2(float *x) {
    if (x[7] <= 2.6500f) {
        return 0.000000f;
    } else {
        if (x[6] <= 38.1500f) {
            if (x[4] <= 82.0500f) {
                return 0.000000f;
            } else {
                return 1.000000f;
            }
        } else {
            return 1.000000f;
        }
    }
}

float tree_3(float *x) {
    if (x[5] <= 9.7500f) {
        if (x[8] <= 7.5500f) {
            if (x[7] <= 2.6500f) {
                return 0.000000f;
            } else {
                return 1.000000f;
            }
        } else {
            if (x[4] <= 82.1500f) {
                if (x[5] <= 6.6500f) {
                    return 1.000000f;
                } else {
                    return 0.000000f;
                }
            } else {
                return 1.000000f;
            }
        }
    } else {
        if (x[4] <= 80.0500f) {
            return 0.000000f;
        } else {
            return 1.000000f;
        }
    }
}

float tree_4(float *x) {
    if (x[7] <= 2.5500f) {
        return 0.000000f;
    } else {
        if (x[5] <= 9.7500f) {
            if (x[2] <= 14.5000f) {
                return 1.000000f;
            } else {
                return 0.000000f;
            }
        } else {
            return 1.000000f;
        }
    }
}

float tree_5(float *x) {
    if (x[4] <= 80.0500f) {
        return 0.000000f;
    } else {
        if (x[4] <= 82.1500f) {
            if (x[2] <= 15.5000f) {
                if (x[5] <= 11.0000f) {
                    return 0.250000f;
                } else {
                    return 1.000000f;
                }
            } else {
                return 1.000000f;
            }
        } else {
            return 1.000000f;
        }
    }
}

float tree_6(float *x) {
    if (x[7] <= 2.5500f) {
        return 0.000000f;
    } else {
        if (x[5] <= 9.8000f) {
            if (x[8] <= 11.6000f) {
                return 1.000000f;
            } else {
                return 0.000000f;
            }
        } else {
            return 1.000000f;
        }
    }
}

float tree_7(float *x) {
    if (x[7] <= 2.6000f) {
        return 0.000000f;
    } else {
        return 1.000000f;
    }
}

float tree_8(float *x) {
    if (x[7] <= 2.5500f) {
        return 0.000000f;
    } else {
        return 1.000000f;
    }
}

float tree_9(float *x) {
    if (x[8] <= 8.7000f) {
        if (x[6] <= 23.4500f) {
            return 0.000000f;
        } else {
            if (x[1] <= 74.5000f) {
                return 0.000000f;
            } else {
                return 1.000000f;
            }
        }
    } else {
        if (x[7] <= 2.5500f) {
            return 0.000000f;
        } else {
            if (x[4] <= 82.0500f) {
                if (x[4] <= 81.6000f) {
                    return 1.000000f;
                } else {
                    return 0.000000f;
                }
            } else {
                return 1.000000f;
            }
        }
    }
}

// Average probability across all trees (matches sklearn's soft-voting exactly).
float wildfire_predict_proba(float *x) {
    float sum = 0.0f;
    sum += tree_0(x);
    sum += tree_1(x);
    sum += tree_2(x);
    sum += tree_3(x);
    sum += tree_4(x);
    sum += tree_5(x);
    sum += tree_6(x);
    sum += tree_7(x);
    sum += tree_8(x);
    sum += tree_9(x);
    return sum / N_TREES;
}

// Returns 1 = fire risk, 0 = no fire risk (threshold at 0.5, matching sklearn).
int wildfire_predict(float *x) {
    return (wildfire_predict_proba(x) > 0.5f) ? 1 : 0;
}

#endif // WILDFIRE_MODEL_H
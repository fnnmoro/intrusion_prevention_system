from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score,
                             confusion_matrix)


def metrics(y_test, pred):
    """Computes the evaluation metrics for a given prediction.

    Parameters
    ----------
    y_test: list
        Test labels that represent the correct answer for the predictions.
    pred: list
        Prediction made by a machine learning model."""

    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()

    outcome = {
        'accuracy': round(accuracy_score(y_test, pred), 5),
        'precision': round(precision_score(y_test, pred), 5),
        'recall': round(recall_score(y_test, pred), 5),
        'f1_score': round(f1_score(y_test, pred), 5),
        'tn': int(tn),
        'fp': int(fp),
        'fn': int(fn),
        'tp': int(tp)
    }

    return outcome

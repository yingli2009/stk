import pytest
import numpy as np
import stk

from .case_data import CaseData


@pytest.fixture(
    params=(
        CaseData(
            periodic_info=stk.PeriodicInfo(
                x_vector=np.array([109.29499828, 0., 0.]),
                y_vector=np.array([18.21583305, 31.54982284, 0.]),
                z_vector=np.array([0., 0., 210.33234855]),
            ),
            x_vector=np.array([109.29499828, 0., 0.]),
            y_vector=np.array([18.21583305, 31.54982284, 0.]),
            z_vector=np.array([0., 0., 210.33234855]),
            a=109.2949982759018,
            b=36.43086458649658,
            c=210.3323485478163,
            alpha=90.0,
            beta=90.0,
            gamma=59.99927221917263,
        ),
    ),
)
def periodic_case(request):

    return request.param

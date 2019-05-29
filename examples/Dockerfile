FROM jupyter/minimal-notebook:abdb27a6dfbb

COPY requirements.txt /tmp/
RUN mkdir /tmp/extra
RUN pip install --requirement /tmp/requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /tmp/extra && \
    fix-permissions /home/$NB_USER

ENV PYTHONPATH=/tmp/extra:${PYTHONPATH}
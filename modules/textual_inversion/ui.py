import html

import gradio as gr

import modules.textual_inversion.textual_inversion
import modules.textual_inversion.preprocess
from modules import sd_hijack, shared


def create_embedding(name, initialization_text, nvpt, overwrite_old, use_negative, nvpt_uc):
    filename = modules.textual_inversion.textual_inversion.create_embedding(name, nvpt, overwrite_old, init_text=initialization_text)
    if use_negative:
        modules.textual_inversion.textual_inversion.create_embedding(name+'-uc', nvpt_uc, overwrite_old, init_text=initialization_text)
        filename=f'{filename} and {filename[:-3]}-uc.pt'

    sd_hijack.model_hijack.embedding_db.load_textual_inversion_embeddings()

    return gr.Dropdown.update(choices=sorted(sd_hijack.model_hijack.embedding_db.word_embeddings.keys())),f"Created: {filename}", ""


def preprocess(*args):
    modules.textual_inversion.preprocess.preprocess(*args)

    return "Preprocessing finished.", ""


def train_embedding(*args):

    assert not shared.cmd_opts.lowvram, 'Training models with lowvram not possible'

    try:
        sd_hijack.undo_optimizations()

        embedding, filename = modules.textual_inversion.textual_inversion.train_embedding(*args)

        res = f"""
Training {'interrupted' if shared.state.interrupted else 'finished'} at {embedding.step} steps.
Embedding saved to {html.escape(filename)}
"""
        return res, ""
    except Exception:
        raise
    finally:
        sd_hijack.apply_optimizations()


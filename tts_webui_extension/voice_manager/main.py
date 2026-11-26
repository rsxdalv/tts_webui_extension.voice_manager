import os

import gradio as gr

from . import store
from .store import (
    ROOT_LABEL,
)
from .store import (
    list_files as get_voice_files,
)
from .store import (
    list_subdirs as get_voice_subdirs,
)


def extension__tts_generation_webui():
    voice_manager_ui()
    return {
        "package_name": "tts_webui_extension.voice_manager",
        "name": "Voice Manager",
        "requirements": "git+https://github.com/rsxdalv/tts_webui_extension.voice_manager@main",
        "description": "Upload, browse, and manage voice reference files for TTS models",
        "extension_type": "interface",
        "extension_class": "tools",
        "author": "danangboy13",
        "extension_author": "danangboy13",
        "license": "MIT",
        "website": "https://github.com/rsxdalv/tts_webui_extension.voice_manager",
        "extension_website": "https://github.com/rsxdalv/tts_webui_extension.voice_manager",
        "extension_platform_version": "0.0.1",
    }


def upload_voices(files, subdir):
    if not files:
        gr.Warning("No files selected for upload.")
        return get_voice_files(subdir)
    count, skipped = store.add_files([getattr(f, "name", f) for f in files], subdir)
    for name in skipped:
        gr.Warning(f"Skipped {name}: unsupported format or name")
    gr.Info(
        f"Uploaded {count} file(s) to voices/{'' if subdir == ROOT_LABEL else subdir}"
    )
    return get_voice_files(subdir)


def delete_voice(subdir, selected_file):
    if not selected_file:
        gr.Warning("No file selected.")
        return get_voice_files(subdir), None, ""
    try:
        if store.remove_file(subdir, selected_file):
            gr.Info(f"Deleted {selected_file}")
        else:
            gr.Warning(f"File not found: {selected_file}")
    except ValueError as e:
        gr.Warning(str(e))
    return get_voice_files(subdir), None, ""


def create_subdirectory(name):
    try:
        created = store.make_subdir(name)
    except (ValueError, FileExistsError) as e:
        gr.Warning(str(e))
        return get_voice_subdirs(), gr.update()
    gr.Info(f"Created subdirectory: {created}")
    return get_voice_subdirs(), gr.update(value=created)


def on_table_select(subdir, evt: gr.SelectData):
    if evt.index[1] != 0:
        return gr.update(), ""
    fname = evt.value
    try:
        fpath = os.path.join(store.resolve_subdir(subdir), fname)
    except ValueError:
        return None, ""
    if store.valid_name(fname) and os.path.isfile(fpath):
        return fpath, fname
    return None, ""


def voice_manager_ui():
    gr.Markdown("## Voice Manager")
    gr.Markdown(
        "Upload, browse, and manage voice reference files for TTS models "
        "(Chatterbox, VibeVoice, Index-TTS, etc.)"
    )

    selected_file_state = gr.State("")

    with gr.Row():
        # Left column - browsing and uploading
        with gr.Column(scale=2):
            with gr.Row():
                subdir_dropdown = gr.Dropdown(
                    label="Subdirectory",
                    choices=get_voice_subdirs(),
                    value="(root)",
                    scale=3,
                )
                refresh_btn = gr.Button("Refresh", size="sm", scale=1)

            with gr.Accordion("Create Subdirectory", open=False), gr.Row():
                new_subdir_input = gr.Textbox(
                    label="New subdirectory name",
                    placeholder="e.g. my-voices",
                    scale=3,
                )
                create_subdir_btn = gr.Button("Create", size="sm", scale=1)

            file_upload = gr.File(
                label="Upload voice files",
                file_types=["audio"],
                file_count="multiple",
            )
            upload_btn = gr.Button("Upload to selected subdirectory", variant="primary")

            file_table = gr.Dataframe(
                headers=["Name", "Size", "Date"],
                datatype=["str", "str", "str"],
                value=get_voice_files("(root)"),
                label="Voice Files",
                interactive=False,
                row_count=(1, "dynamic"),
            )

        # Right column - preview and actions
        with gr.Column(scale=1):
            audio_preview = gr.Audio(
                label="Audio Preview",
                type="filepath",
                interactive=False,
            )
            file_info = gr.Textbox(
                label="Selected File",
                interactive=False,
                placeholder="Click a filename in the table to preview",
            )
            delete_btn = gr.Button("Delete Selected File", variant="stop")

    # Event handlers
    def refresh_all(subdir):
        return gr.update(choices=get_voice_subdirs()), get_voice_files(subdir)

    refresh_btn.click(
        fn=refresh_all,
        inputs=[subdir_dropdown],
        outputs=[subdir_dropdown, file_table],
    )

    subdir_dropdown.change(
        fn=get_voice_files,
        inputs=[subdir_dropdown],
        outputs=[file_table],
    ).then(
        fn=lambda: (None, ""),
        outputs=[audio_preview, file_info],
    )

    create_subdir_btn.click(
        fn=create_subdirectory,
        inputs=[new_subdir_input],
        outputs=[subdir_dropdown, subdir_dropdown],
    ).then(
        fn=get_voice_files,
        inputs=[subdir_dropdown],
        outputs=[file_table],
    )

    upload_btn.click(
        fn=upload_voices,
        inputs=[file_upload, subdir_dropdown],
        outputs=[file_table],
    )

    file_table.select(
        fn=on_table_select,
        inputs=[subdir_dropdown],
        outputs=[audio_preview, selected_file_state],
    )

    selected_file_state.change(
        fn=lambda x: x,
        inputs=[selected_file_state],
        outputs=[file_info],
    )

    delete_btn.click(
        fn=delete_voice,
        inputs=[subdir_dropdown, selected_file_state],
        outputs=[file_table, audio_preview, selected_file_state],
    )


if __name__ == "__main__":
    # Run standalone with: python -m tts_webui_extension.voice_manager.main
    with gr.Blocks() as demo, gr.Tab("Voice Manager"):
        voice_manager_ui()
    demo.launch(server_port=7771)

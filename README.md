# Voice Manager (TTS WebUI extension)

Upload, browse, preview and delete voice reference clips (`.wav .mp3 .flac .ogg .m4a .opus`) in the
`voices/` folder of [TTS WebUI](https://github.com/rsxdalv/TTS-WebUI). Clips can be sorted into
subfolders. The clips are used by cloning engines such as Chatterbox, VibeVoice and Index-TTS.

Original code by danangboy13 (TTS-WebUI PR #650). Packaged as an external extension, with path checks,
no-overwrite uploads and tests added.

## Install

Add it to `extensions.external.json` in the TTS WebUI root (see `documentation/external_extensions.md`):

```json
{
  "tabs": [
    {
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
      "extension_platform_version": "0.0.1"
    }
  ]
}
```

It is a Gradio tab, so it needs the Gradio host. The voices folder is `$TTS_WEBUI_VOICES_DIR` if set,
otherwise `./voices` in the folder the app runs from.

## Develop

```
pip install -e ".[test]"
pytest
python -m tts_webui_extension.voice_manager.main   # standalone on port 7771
```

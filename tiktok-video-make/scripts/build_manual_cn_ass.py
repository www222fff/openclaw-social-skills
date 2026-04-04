#!/usr/bin/env python3
"""Build a Chinese ASS subtitle file from an existing ASS timing track and manual translations.

Usage:
  python3 build_manual_cn_ass.py template <source.ass> [template.json]
  python3 build_manual_cn_ass.py build <source.ass> <translations.json|txt> [output.ass]

Template JSON format:
[
  {"index": 1, "start": "0:00:00.00", "end": "0:00:04.00", "source": "Some people...", "translated": ""}
]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from subtitle_utils import ass_text_to_plain, parse_ass_dialogues, write_translated_ass


def export_template(ass_path: str | Path, output_path: str | Path | None = None) -> str:
    ass_path = Path(ass_path)
    output_path = Path(output_path) if output_path else ass_path.with_suffix('.manual_translation.json')

    _, dialogues = parse_ass_dialogues(ass_path)
    rows = []
    for idx, dialogue in enumerate(dialogues, start=1):
        rows.append({
            'index': idx,
            'start': dialogue.raw_prefix_fields[1],
            'end': dialogue.raw_prefix_fields[2],
            'source': ass_text_to_plain(dialogue.text),
            'translated': '',
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f'📝 Translation template written: {output_path}')
    return str(output_path)


def _load_translations(path: str | Path) -> list[str]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Translation file not found: {path}')

    if path.suffix.lower() == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError('Translation JSON must be a list')

        translations: list[str] = []
        for item in data:
            if isinstance(item, str):
                translations.append(item.strip())
            elif isinstance(item, dict):
                value = item.get('translated') or item.get('text') or item.get('cn') or ''
                translations.append(str(value).strip())
            else:
                raise ValueError(f'Unsupported translation item: {item!r}')
        return translations

    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    return [line for line in lines if line]


def build_manual_cn_ass(ass_path: str | Path, translations_path: str | Path,
                        output_path: str | Path | None = None) -> str:
    ass_path = Path(ass_path)
    output_path = Path(output_path) if output_path else ass_path.with_name(f'{ass_path.stem}_cn.ass')
    sidecar_path = output_path.with_suffix('.json')

    header, dialogues = parse_ass_dialogues(ass_path)
    translations = _load_translations(translations_path)

    if len(dialogues) != len(translations):
        raise ValueError(
            f'Translation count mismatch: ASS has {len(dialogues)} dialogue lines, '
            f'but translation file has {len(translations)} entries'
        )

    empty_indexes = [str(i + 1) for i, text in enumerate(translations) if not text]
    if empty_indexes:
        raise ValueError('Empty translations found at rows: ' + ', '.join(empty_indexes[:20]))

    write_translated_ass(header, dialogues, translations, output_path, sidecar_json_path=sidecar_path)
    print(f'✅ Chinese ASS written: {output_path}')
    print(f'📝 Sidecar written: {sidecar_path}')
    return str(output_path)


def main():
    if len(sys.argv) < 3:
        print('Usage:')
        print('  python3 build_manual_cn_ass.py template <source.ass> [template.json]')
        print('  python3 build_manual_cn_ass.py build <source.ass> <translations.json|txt> [output.ass]')
        sys.exit(1)

    mode = sys.argv[1]
    if mode == 'template':
        source_ass = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
        export_template(source_ass, output)
        return

    if mode == 'build':
        if len(sys.argv) < 4:
            print('Usage: python3 build_manual_cn_ass.py build <source.ass> <translations.json|txt> [output.ass]')
            sys.exit(1)
        source_ass = sys.argv[2]
        translations = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
        build_manual_cn_ass(source_ass, translations, output)
        return

    raise SystemExit(f'Unknown mode: {mode}')


if __name__ == '__main__':
    main()

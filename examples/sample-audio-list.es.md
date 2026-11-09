# Audio recording list: Spanish sample

This is the specification for the audio generator: **8 files to produce**.

## Rules for the generator

1. One MP3 per ID. Save every file at the path in its *Save as* column, under the unit's folder.
2. Rows that say "no new file" repeat an earlier recording and are not generated.
3. `M` = male voice, `F` = female voice, `F+M` = a dialogue (one voice per speaker).
4. Texts, sentences and phrases are generated at 0.8x speed (see each heading); vocabulary at normal speed.

## Voices (edge-tts)

| Code | Voice | Use |
|---|---|---|
| ES-F1 | `es-ES-ElviraNeural` | Default female (Spain) |
| ES-M1 | `es-ES-AlvaroNeural` | Default male (Spain) |
| LA-F1 | `es-MX-DaliaNeural` | Female, Latin American variety |
| LA-M1 | `es-MX-JorgeNeural` | Male, Latin American variety |

## Unit 1: Primer contacto

Folder: `lo-01-primer-contacto/`

### A. Vocabulary: one word or phrase per file

| ID | Spanish | English | Voice | Save as | Where |
|---|---|---|---|---|---|
| U01-A-V01 | ¡Hola! | Hello | F | `vocab/U01-A-V01.mp3` | Topic A |
| U01-A-V02 | Buenos días | Good morning | M | `vocab/U01-A-V02.mp3` | Topic A |
| U01-A-V03 | ¡Hola! | Hello | F | no new file: uses **U01-A-V01** | Topic A |

### B. Texts and dialogues (generate at 0.8x speed)

| ID | Where | Voice | Save as | Voice note | Text |
|---|---|---|---|---|---|
| U01-B-T1 | Dialogue: formal greeting | **F+M** | `texts/U01-B-T1.mp3` | Sra. Martínez = F, Sr. González = M | Sra. Martínez: Buenos días, señor González. ¿Cómo está? / Sr. González: Muy bien, gracias, señora Martínez. ¿Y usted? |
| U01-B-T2 | Reading: Marta | F | `texts/U01-B-T2.mp3` |  | Me llamo Marta. Soy de Madrid. ¶ Vivo con mi familia. |

### C. Exercise sentences (generate at 0.8x speed)

| ID | Exercise | Voice | Save as | Voice note | Sentence |
|---|---|---|---|---|---|
| U01-C-S01 | Ex. 1 | M | `sentences/U01-C-S01.mp3` |  | Me llamo … |
| U01-C-S02 | Ex. 1 | F | `sentences/U01-C-S02.mp3` | LA-F1, Mexican variety | ¿Cómo te llamas? |

## Unit 2: Los números

Folder: `lo-02-los-numeros/`

### A. Vocabulary: one word or phrase per file

| ID | Spanish | English | Voice | Save as | Where |
|---|---|---|---|---|---|
| U02-A-V01 | uno | one | M | `vocab/U02-A-V01.mp3` | Topic A |
| U02-A-V02 | dos | two | F | `vocab/U02-A-V02.mp3` | Topic A |

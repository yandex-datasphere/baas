import requests
from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage

BASE_URL = "https://art.ycloud.eazify.net:8443/biorandom" 
MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84] 
TEMPO_BPM = 200  # Темп в ударах в минуту
N_NOTES = 32 # Количество нот в композиции

def fetch_bio_numbers(n: int) -> list[int]: 
    print(f"Запрашиваем {n} биочисел...")
    try:
        response = requests.get(f"{BASE_URL}/get/{n}", timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return []
    
    data = response.json()
    if not isinstance(data, list) or not all("num" in item for item in data):
        raise ValueError("Неверный формат данных от API")
    return [item["num"] for item in data]

def generate_chord(note: int, chord_type='major') -> list[int]:
    if chord_type == 'major':
        return [note, note + 4, note + 7]
    elif chord_type == 'minor':
        return [note, note + 3, note + 7]
    else:
        raise ValueError(f"Неизвестный тип аккорда: {chord_type}")

def get_duration(i: int, numbers: list[int], ticks_per_beat: int) -> int:
    return ticks_per_beat if numbers[(i + 2) % len(numbers)] % 3 == 0 else ticks_per_beat // 2

def get_velocity(num: int) -> int:
    return 50 + (num * 3) % 78

def create_midi(numbers: list[int], output="bio_music.mid", tempo_bpm=TEMPO_BPM):
    print("Создаём MIDI-файл...")
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    tempo = bpm2tempo(tempo_bpm)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    ticks_per_beat = mid.ticks_per_beat

    for i, num in enumerate(numbers):
        note = MAJOR_SCALE[num % len(MAJOR_SCALE)]
        is_chord = numbers[(i + 1) % len(numbers)] % 2 == 0

        if is_chord:
            chord = generate_chord(note)
            duration = get_duration(i, numbers, ticks_per_beat)
            velocity = get_velocity(num)

            for chord_note in chord:
                track.append(Message('note_on', note=chord_note, velocity=velocity, time=0))
            track.append(Message('note_off', note=chord[0], velocity=64, time=duration))
        else:
            duration = get_duration(i, numbers, ticks_per_beat)
            velocity = get_velocity(num)

            track.append(Message('note_on', note=note, velocity=velocity, time=0))
            track.append(Message('note_off', note=note, velocity=64, time=duration))

    mid.save(output)
    print(f"Готово! Файл сохранён как: {output}")

def main():
    n_notes = N_NOTES
    numbers = fetch_bio_numbers(n_notes)
    print("Биочисла:", numbers)
    create_midi(numbers)

if __name__ == "__main__":
    main()


# Mini Redis

Python으로 Redis의 핵심 원리를 직접 구현하는 **CLI 기반 In-Memory Key-Value 저장소** 학습 프로젝트입니다.

`dict`, `set`, `collections`를 저장소 구현에 이용하지 않고 **해시맵(체이닝), 이중 연결 리스트, 최소 힙**을 직접 구현하여 빠른 조회, LRU 메모리 제거, TTL 만료 처리를 학습합니다.

> 실제 Redis 서버가 아닌 교육용 단일 프로세스 프로그램입니다. 네트워크 통신, 데이터 영속성, 동시성 기능은 제공하지 않습니다.

## 1. 실행 방법

필요 환경: **Python 3.8 이상**. 외부 패키지 설치는 필요하지 않습니다.

```bash
git clone https://github.com/SeouliteParker/Mini_Redis.git
cd Mini_Redis
python3 main.py
```

Windows에서는 `python main.py` 또는 `py main.py`를 사용할 수 있습니다.

```text
Mini Redis 실행!
종료하려면 exit 또는 quit 입력
mini-redis> SET name "Alice"
OK
mini-redis> GET name
"Alice"
mini-redis> DBSIZE
(integer) 1
mini-redis> exit
Mini Redis 종료
```

한 줄씩 명령을 입력하며, `exit` 또는 `quit`으로 종료합니다. 입력 파싱에는 Python 표준 라이브러리 `shlex`를 사용하므로 큰따옴표로 둘러싼 값도 사용할 수 있습니다.

## 2. 프로젝트 파일 구조

```text
Mini_Redis/
├── main.py              # CLI(REPL), 명령어 파싱 및 오류 메시지
├── mini_redis.py        # Key-Value 저장, LRU, TTL, 메모리 정책
├── hash_map.py          # 해시맵: 해시 함수·체이닝·버킷 확장
├── doubly_linked.py     # 이중 연결 리스트: 노드 삽입·삭제·이동
├── min_heap.py          # 최소 힙: TTL 만료 시각 관리
├── .gitignore           # Python 캐시 파일 추적 제외
└── README.md            # 프로젝트 설명 문서
```

## 3. 직접 구현한 세 자료구조

### 해시맵(HashMap)

`key`라는 이름으로 `value`를 저장하고 검색하는 구조입니다. `hash_map.py`는 각 문자에 대해 `hash_value = hash_value * 31 + ord(char)`를 반복한 후 버킷 수로 나눈 나머지로 위치를 정합니다.

- **버킷(bucket)**: 해시 함수가 지정한 저장 칸입니다.
- **체이닝(chaining)**: 다른 키가 같은 버킷을 가리킬 때 이중 연결 리스트로 여러 항목을 연결해 보관합니다.
- **로드 팩터(load factor)**: `저장된 항목 수 / 버킷 수`입니다. **0.75를 초과하면** 버킷 수를 두 배로 늘리고 기존 항목의 위치를 다시 계산합니다.
- 평균적인 조회·저장·삭제는 O(1)을 기대하지만, 충돌이 심하면 버킷 연결 리스트를 순차 탐색해야 하므로 최악의 경우 O(n)입니다.

### 이중 연결 리스트(DoublyLinkedList)

각 `Node`에는 `data`, 이전 노드를 참조하는 `prev`, 다음 노드를 참조하는 `next`가 있습니다. `head`는 첫 노드, `tail`은 마지막 노드를 가리킵니다.

- `insert_front`, `insert_back`: 앞/뒤에 삽입
- `remove_front`, `remove_back`: 앞/뒤 노드 삭제
- `remove_node`: 이미 알고 있는 노드 삭제
- `move_to_front`: 이미 알고 있는 노드를 가장 앞으로 이동

노드를 **이미 알고 있는 경우** 위 삽입·삭제·이동은 O(1)입니다. Mini Redis에서는 별도 해시맵 `lru_nodes`에 `key → Node`를 저장해 빠르게 노드를 찾습니다.

### 최소 힙(MinHeap)

가장 이른 만료 시각이 맨 위(`peek`)에 오도록 유지하는 자료구조입니다. `(expire_at, key)` 형태로 저장합니다.

- `push`: 추가 후 `_heapify_up`으로 정리 — O(log n)
- `peek`: 가장 이른 만료 항목 확인 — O(1)
- `pop`: 가장 이른 항목 제거 후 `_heapify_down`으로 정리 — O(log n)
- 배열 공간이 부족하면 저장 공간을 두 배로 확장합니다.

## 4. LRU: 오래 사용하지 않은 데이터부터 삭제

**LRU(Least Recently Used)**는 메모리 한도를 넘었을 때 가장 오랫동안 사용하지 않은 키부터 제거하는 정책입니다.

1. `SET` 또는 성공한 `GET`으로 사용한 키를 이중 연결 리스트의 **맨 앞(head)** 으로 이동합니다.
2. `CONFIG SET maxmemory 20`처럼 메모리 한도를 설정할 수 있습니다.
3. `SET` 이후 사용량이 한도를 초과하면 **맨 뒤(tail)** 키부터 삭제합니다.
4. LRU 정책으로 삭제한 건수는 `evicted_keys`에 누적됩니다.
5. 단일 키+값 자체가 메모리 한도를 초과한다면 저장하지 않고 OOM 오류를 반환합니다.

**메모리 사용량 기준:**

```text
used_memory = Σ(키의 UTF-8 바이트 길이 + 값의 UTF-8 바이트 길이)
```

Python 객체·노드·버킷의 실제 메모리 오버헤드는 계산하지 않습니다.

**예시:**

```text
mini-redis> CONFIG SET maxmemory 20
OK
mini-redis> SET A 12345
OK
mini-redis> SET B 12345
OK
mini-redis> SET C 12345
OK
mini-redis> GET A
"12345"
mini-redis> SET D 123645
OK
mini-redis> KEYS
1. "A"
2. "C"
3. "D"
mini-redis> INFO memory
used_memory:19
maxmemory:20
evicted_keys:1
```

`KEYS`의 출력 순서는 달라질 수 있습니다. A와 C는 각각 6바이트, D는 7바이트로 합계가 19바이트입니다. B가 LRU 정책으로 제거됩니다.

## 5. TTL: 유효기간이 지난 데이터 처리

**TTL(Time To Live)**은 키가 살아 있는 시간을 초 단위로 정합니다.

- `EXPIRE key seconds`: 키의 만료 시각을 설정합니다.
- `TTL key`: 남은 유효시간을 반환합니다.
- `TTL` 반환값 `-1`: 키는 있지만 만료 기한 없음.
- `TTL` 반환값 `-2`: 키가 존재하지 않거나 이미 만료됨.
- `SET`으로 기존 값을 덮어쓰면 이전 TTL은 초기화됩니다.

키를 조회하기 전에 해당 키의 만료를 검사합니다. 또한 `INFO memory`, `DBSIZE`, `KEYS`, 메모리 자동 제거 전에 최소 힙을 통해 만료된 항목을 정리합니다. 별도의 상시 백그라운드 스레드가 만료를 처리하지는 않습니다.

### Lazy Deletion(지연 삭제)

같은 키에 `EXPIRE`를 여러 번 실행하면 힙에 **이전 만료 시각 기록이 남을 수 있습니다**. 이 기록을 즉시 삭제하는 대신, 힙에서 꺼낼 때 해시맵에 저장된 **현재 유효한 만료 시각**과 비교합니다. 둘이 일치할 때만 키를 삭제하므로 이전 설정이 현재 데이터를 지우지 않습니다.

## 6. 지원 명령어 10개

| 명령어 | 예시 | 기능 |
|---|---|---|
| `SET` | `SET user:1 Alice` | 값 저장/덮어쓰기 |
| `GET` | `GET user:1` | 값 조회 |
| `DEL` | `DEL user:1` | 키 삭제 |
| `EXISTS` | `EXISTS user:1` | 키 존재 여부(0 또는 1) |
| `DBSIZE` | `DBSIZE` | 키 개수 |
| `KEYS` | `KEYS` | 전체 키 목록(패턴 없음) |
| `CONFIG SET maxmemory` | `CONFIG SET maxmemory 20` | 메모리 한도(바이트, 0은 무제한) |
| `INFO memory` | `INFO memory` | 사용량·한도·LRU 제거 수 |
| `EXPIRE` | `EXPIRE user:1 60` | 유효기간 설정(초) |
| `TTL` | `TTL user:1` | 남은 유효기간 조회 |

출력은 `OK`, `(nil)`, `(integer) N`, `(error) ...` 같은 Redis 스타일 형식을 따릅니다.

## 7. 직접 실행하여 확인한 테스트

아래는 개발 중 **실제 터미널 출력으로 확인된 시나리오**입니다. 자동화된 전체 테스트 스위트가 구축되었다는 뜻은 아닙니다.

| 테스트 | 확인 내용 |
|---|---|
| 해시맵 자동 확장 | 8개 버킷에서 7번째 데이터 저장 시 16개로 확장, 기존 키 조회 정상 |
| 해시 충돌·체이닝 | `AB`, `AJ`가 같은 1번 버킷, 개별 조회·삭제 정상 |
| LRU | `GET A` 후 새 데이터 추가 시 오래된 `B` 삭제, `evicted_keys:1` |
| 메모리 계산 | A·C·D 합계 19바이트 정확히 표시 |
| OOM | 20바이트 제한에 23바이트의 `BUG` 엔트리 저장 거절, 기존 A·B 유지 |
| TTL 만료 | 만료된 A 조회 `(nil)`, `TTL A`는 -2, 메모리 6바이트 남음 |
| 반복 EXPIRE | 2초 → 120초 갱신 후 3초 경과 시 값 유지, TTL 약 116초 |
| 삭제 연동 | `DEL A` 후 `EXISTS A = 0`, `TTL A = -2`, B만 남음 |
| 오류 처리 | 알 수 없는 명령, 인자 개수 오류, 정수 변환 오류 정상 반환 |
| 시작 출력 개선 | 이중 연결 리스트의 독립 테스트 코드를 `if __name__ == "__main__":` 아래로 이동 |

## 8. 한계 및 추가 검증 과제

- 단일 프로세스 CLI만 지원하며 네트워크 서버 기능은 없습니다.
- 실행 종료 시 데이터는 사라지고 파일로 저장하지 않습니다.
- Redis의 List/Set/Sorted Set 같은 복합 자료형은 구현하지 않습니다.
- 실제 운영 환경처럼 대용량 데이터, 장기 실행, 충돌 집중 상황의 성능을 측정하지 않았습니다.
- 자동화 단위 테스트와 경계 조건(반복 덮어쓰기, 빈 키 목록, 다량의 TTL 갱신 등)은 추가 작성이 필요합니다.

## 9. 학습 핵심 정리

> **해시맵은 데이터를 찾고, 이중 연결 리스트는 사용 순서를 기억하며, 최소 힙은 가장 빠른 만료 시각을 찾습니다.**
>
> 세 자료구조를 결합하여 빠른 조회, LRU 캐시 제거, TTL 만료 관리를 구현하는 것이 이 프로젝트의 핵심입니다.
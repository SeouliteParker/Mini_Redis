# Mini Redis 테스트 검증 보고서

> 프로젝트: [SeouliteParker/Mini_Redis](https://github.com/SeouliteParker/Mini_Redis)  
> 기준일: 2026-11-07 (KST)  
> 검증 방식: Python 표준 라이브러리 `unittest` 자동화 테스트  
> 결과: **19건 실행 / 19건 통과 / 실패 0건 / 오류 0건**

## 1. 검증 목적과 증빙 자료

이 보고서는 **「정보를 엄청 빠르게 찾아주는 작은 저장소 만들기」** 미션의 필수 기능이 구현되었는지 확인한 자동화 테스트 결과를 정리한다. 설명만으로 완료를 주장하지 않고, 평가자가 소스와 실행 결과를 확인하고 직접 재현할 수 있도록 다음 자료를 제공한다.

| 증빙 | 파일 | 용도 |
|---|---|---|
| 1. 테스트 코드 | [test_mini_redis.py](test_mini_redis.py) | 19개 테스트의 입력, 검증 조건, 기대값 |
| 2. 실행 로그 | [tests/test_results.txt](tests/test_results.txt) | 실제 실행 시 각 테스트의 `ok` 및 최종 `OK` |
| 3. 검증 보고서 | [TEST_REPORT.md](TEST_REPORT.md) | 미션 요구사항별 검증 근거 및 한계 |

**검증 대상 구현:** `main.py`, `mini_redis.py`, `hash_map.py`, `doubly_linked.py`, `min_heap.py`.

## 2. 테스트 환경과 재현 방법

- 실행 환경: macOS 터미널에서 Python 3으로 실행한 사용자 제공 로그
- 실행 도구: Python 표준 라이브러리 `unittest` (`unittest.mock.patch` 포함)
- 외부 테스트 패키지: 없음
- 테스트 대상: CLI 명령 파서 및 Mini Redis 클래스와 세 자료구조
- **주의:** 로그에서 정확한 Python 마이너 버전 및 하드웨어 사양까지 확인된 것은 아니다.

저장소 최상위 폴더에서 실행:

```bash
python3 -m unittest -v test_mini_redis
```

실행 로그를 새로 저장할 때:

```bash
mkdir -p tests
python3 -m unittest -v test_mini_redis > tests/test_results.txt 2>&1
cat tests/test_results.txt
```

> 시간 경과가 필요한 TTL 테스트는 `unittest.mock.patch("mini_redis.time.time", ...)`로 시각을 고정하여 실행했다. 따라서 테스트가 빠르게 완료되어도 만료 전후 로직을 결정적으로 검증한다.

## 3. 실제 실행 결과

아래 결과는 사용자가 로컬 터미널에서 직접 실행하여 확인한 내용이며, [원본 로그](tests/test_results.txt)에 전체 19건의 테스트 이름과 결과가 보관되어 있다.

```text
----------------------------------------------------------------------
Ran 19 tests in 0.003s

OK
```

| 지표 | 관측 결과 |
|---|---:|
| 실행 테스트 | 19 |
| 통과 | 19 |
| 실패 | 0 |
| 오류 | 0 |
| 실행 시간 | 0.003초 (해당 로그 기준) |

## 4. 테스트 케이스별 검증 결과 (19/19)

| # | 테스트 함수 | 검증 내용 | 결과 |
|---:|---|---|---|
| 1 | `test_insert_move_remove` | 이중 연결 리스트의 앞·뒤 삽입, 노드 이동·삭제, head/tail 및 길이 갱신 | PASS |
| 2 | `test_collision_and_individual_deletion` | 해시 충돌(AB/AJ), 체이닝 조회, 한 키 삭제 후 다른 키 유지 | PASS |
| 3 | `test_resize_rehash_and_overwrite` | 7개 입력 시 8→16 버킷 확장, 재해싱, 기존 값 덮어쓰기 | PASS |
| 4 | `test_minimum_first_and_capacity_growth` | 최소 힙 순서, peek/pop, 4→8 배열 용량 확장, 빈 힙 처리 | PASS |
| 5 | `test_basic_set_get_del_exists` | SET/GET/DEL/EXISTS 및 삭제된 키 반환값 | PASS |
| 6 | `test_dbsize_and_keys` | 빈 저장소 및 복수 키의 개수·목록 | PASS |
| 7 | `test_utf8_memory_accounting_and_overwrite` | 한글 UTF-8 바이트 합산 및 덮어쓰기 후 사용량 | PASS |
| 8 | `test_lru_eviction_order` | GET으로 최근 사용 키 갱신, 메모리 초과 시 LRU 제거 및 누적 횟수 | PASS |
| 9 | `test_oom_does_not_modify_existing_keys` | 단일 항목이 한도 초과 시 OOM, 기존 데이터 보존 | PASS |
| 10 | `test_config_zero_unlimited_and_invalid` | maxmemory=0 및 음수 설정 오류 | PASS |
| 11 | `test_ttl_no_expiry_and_missing` | 미존재 키 TTL=-2, 만료 기한 없는 키 TTL=-1, 없는 키 EXPIRE=0 | PASS |
| 12 | `test_ttl_expiration_removes_key_and_memory` | 시간 경과 후 키·메모리 제거 | PASS |
| 13 | `test_expire_zero_deletes_immediately` | EXPIRE 0의 즉시 삭제 | PASS |
| 14 | `test_set_overwrite_clears_ttl` | SET 덮어쓰기 시 기존 TTL 초기화 | PASS |
| 15 | `test_repeated_expire_ignores_stale_heap_entry` | EXPIRE 재설정 후 이전 힙 기록으로 오삭제되지 않음 | PASS |
| 16 | `test_delete_cleans_expiry_and_lru` | DEL 후 데이터·LRU 참조·TTL 참조·메모리 정리 | PASS |
| 17 | `test_info_memory_fields` | used_memory, maxmemory, evicted_keys 필드 출력 | PASS |
| 18 | `test_quotes_and_command_parsing` | 따옴표로 묶인 공백 포함 값, CLI 파싱 | PASS |
| 19 | `test_invalid_commands_and_arguments` | 미지원 명령, 인자 부족, 정수 오류, 닫히지 않은 따옴표 | PASS |

## 5. 필수 미션 요구사항별 증빙 연결

| 미션 요구사항 | 확인 방법 / 대표 테스트 |
|---|---|
| 이중 연결 리스트: O(1) 삽입·삭제·이동 | `test_insert_move_remove`; 코드는 직접 노드 참조를 연결/해제함. **성능 시간복잡도 실측은 아님** |
| 해시맵: 자체 해시·체이닝·0.75 초과 확장 | `test_collision_and_individual_deletion`, `test_resize_rehash_and_overwrite` |
| 최소 힙: push/pop/peek/heapify | `test_minimum_first_and_capacity_growth` |
| String 6개 명령어 | `test_basic_set_get_del_exists`, `test_dbsize_and_keys` |
| CONFIG SET maxmemory / INFO memory | `test_config_zero_unlimited_and_invalid`, `test_info_memory_fields` |
| UTF-8 기반 used_memory 계산 | `test_utf8_memory_accounting_and_overwrite` |
| LRU 갱신·자동 삭제·evicted_keys | `test_lru_eviction_order` |
| 단일 엔트리 초과 시 OOM | `test_oom_does_not_modify_existing_keys` |
| EXPIRE / TTL 및 만료 후 없는 키 처리 | `test_ttl_no_expiry_and_missing`, `test_ttl_expiration_removes_key_and_memory`, `test_expire_zero_deletes_immediately` |
| TTL 덮어쓰기·재설정·DEL 연동 | `test_set_overwrite_clears_ttl`, `test_repeated_expire_ignores_stale_heap_entry`, `test_delete_cleans_expiry_and_lru` |
| REPL 명령 파싱 및 에러 메시지 | `test_quotes_and_command_parsing`, `test_invalid_commands_and_arguments`; 실제 대화형 REPL 종료 동작은 별도 수동 확인 범위 |
| 구현 제약: dict/set/collections 금지 | 주요 저장소 구현 파일을 소스 검토. **이 항목은 실행 테스트 19건으로 직접 증명한 것은 아님** |

## 6. 대표 검증 시나리오

### 6.1 해시 충돌과 체이닝

`AB`와 `AJ`는 초기 8개 버킷에서 같은 위치로 계산된다. 두 키를 저장한 뒤 `AB`만 삭제해도 `AJ` 값이 유지되는지 검증했다.

### 6.2 메모리 제한과 LRU

`maxmemory=20`에서 A·B·C를 저장하고 A를 GET한 뒤 D를 저장한다. 가장 오랫동안 사용하지 않은 B가 제거되며 `used_memory=19`, `evicted_keys=1`인지 검증했다.

### 6.3 TTL 갱신 시 오래된 힙 기록 무시

모의 시각 1000초에 A의 만료 시간을 2초로 설정한 직후 120초로 재설정한다. 모의 시각 1003초에도 A가 살아 있고 TTL이 117초인지 확인하여 지연 삭제의 안전성을 검증했다.

### 6.4 OOM 실패 시 기존 데이터 보존

`maxmemory=20`에서 A와 B를 저장한 뒤 용량을 넘는 BUG 엔트리를 저장하려고 한다. 오류가 반환되고 A·B의 메모리 합계 12바이트 및 제거 카운터 0이 유지되는지 확인했다.

## 7. 검증 범위와 한계

- **확인됨:** 위 19개 자동 테스트가 제출된 실행 로그에서 모두 PASS.
- **별도 실측 없음:** 대량 데이터 성능, O(1) 시간복잡도 실측, 장시간 실행 시 힙의 이전 만료 기록 누적 영향.
- **별도 자동화되지 않음:** CLI 프로그램 전체를 대화형 프로세스로 실행해 `exit`/`quit` 종료를 검증하는 종단 간 테스트.
- **주의:** 예제에 포함된 `unittest.mock.patch` 시간 조작은 실제로 수 초를 대기했다는 뜻이 아님.
- **범위 외:** 보너스 과제(동적 배열 직접 구현, 스택/큐/덱, 트리, BST, Pub/Sub).

## 8. 종합 판정

**기록된 19개 자동화 테스트가 모두 통과했다.** 따라서 이 테스트들이 다루는 필수 자료구조와 Mini Redis 기능이 구현된 상태임을 재현 가능한 방식으로 입증한다. 다만 전체 요구사항의 모든 가능한 입력·성능 특성을 증명한 것으로 해석해서는 안 된다.

평가자는 저장소 루트에서 `python3 -m unittest -v test_mini_redis`를 실행하여 동일한 검증을 재현할 수 있다.

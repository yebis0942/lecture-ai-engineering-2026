"""宿題（実装）: 検索結果に前後ページを付ける処理のテスト（APIキー不要）。"""

from app.retrieval import add_neighbors, load_pages


def _page(document_id, page):
    return {"page_id": f"{document_id}-p{page:03d}", "document_id": document_id,
            "section": "章", "title": f"{document_id} p.{page}", "page": page,
            "content": f"本文 {document_id} {page}"}


PAGES = [*(_page("lec01-main", n) for n in range(1, 4)),
         *(_page("lec02-main", n) for n in range(1, 6))]


def _hit(document_id, page):
    return {**_page(document_id, page), "distance": 0.1}


def _neighbor_ids(result):
    return [n["page_id"] for n in result["neighbors"]]


def test_window_zero_keeps_results_unchanged():
    hits = [_hit("lec02-main", 3)]
    assert add_neighbors(hits, PAGES, 0) == hits


def test_adds_previous_and_next_page():
    [result] = add_neighbors([_hit("lec02-main", 3)], PAGES, 1)
    assert _neighbor_ids(result) == ["lec02-main-p002", "lec02-main-p004"]
    assert [n["relation"] for n in result["neighbors"]] == ["前のページ", "次のページ"]
    assert result["neighbors"][0]["content"] == "本文 lec02-main 2"


def test_does_not_cross_documents():
    # lec02の1ページ目の前は lec01 の最終ページだが、資料が違うので付けない
    first, last = add_neighbors([_hit("lec02-main", 1), _hit("lec01-main", 3)], PAGES, 1)
    assert _neighbor_ids(first) == ["lec02-main-p002"]
    assert _neighbor_ids(last) == ["lec01-main-p002"]


def test_no_duplicates_with_hits_or_other_neighbors():
    # p.3とp.4が両方ヒット: 互いを前後ページとして付けず、p.5は上位の結果にだけ付く
    results = add_neighbors([_hit("lec02-main", 4), _hit("lec02-main", 3), _hit("lec02-main", 5)], PAGES, 1)
    assert [_neighbor_ids(r) for r in results] == [[], ["lec02-main-p002"], []]
    all_ids = [r["page_id"] for r in results] + [i for r in results for i in _neighbor_ids(r)]
    assert len(all_ids) == len(set(all_ids))


def test_real_materials_lora_page_gets_neighbors():
    pages = load_pages()
    [result] = add_neighbors([{**next(p for p in pages if p["page_id"] == "lec02-main-p052"),
                               "distance": 0.1}], pages, 1)
    assert _neighbor_ids(result) == ["lec02-main-p051", "lec02-main-p053"]

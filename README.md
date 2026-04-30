Impor Massal Tugas ke Taiga Sprint

Deskripsi
- Alur impor massal tugas dari dokumen PDF atau DOC/DOCX ke Taiga Self-Hosted Sprint.
- Input dokumen harus melalui proses ekstraksi teks jika berbentuk PDF.
- Menerapkan kepatuhan ISO 27001 (audit trail, akses terbatas, logging insiden).

Format & Mapping
- Dokumen input (PDF/DOC/DOCX) diekstraksi menjadi data tugas dengan struktur:
  Talent → assignee Taiga (penugasan)
  Note → judul tugas
  Estimation → estimasi waktu/usaha
- User Stories disetel kosong (placeholder jika API Taiga mengharuskan field tersebut).

Taiga Self-Hosted
- Gunakan Taiga Self-Hosted: set taiga_url ke root API Taiga self-hosted (mis. https://taiga.yourdomain/api/v1).
- Token API harus dengan hak akses least privilege dan tidak disimpan di kode sumber.

Contoh Dokument
- Dokumen TXT contoh: docs/samples/ImporMassalTaigaSprint_SampleInput.txt
- Dokument contoh lengkap: docs/samples/ImporMassalTaigaSprint_SampleDocument.txt
- Output contoh: docs/samples/ImporMassalTaigaSprint_OutputSample.json

Paket Standar
- taiga-push.yml berisi blueprint flow untuk CI/CD/perangkat orkestrasi internal.
- Panduan ekstraksi PDF ke TXT disediakan di dokumentasi terkait.

Kontak
- Hubungi tim DevOps/Platform untuk bantuan implementasi lebih lanjut.

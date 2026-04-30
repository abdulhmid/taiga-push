# Impor Massal Tugas ke Taiga Sprint - Panduan Pengguna

Dokumen ini menjelaskan alur kerja, format input, dan praktik kepatuhan untuk impor massal tugas ke Taiga Sprint menggunakan dokumen berformat PDF atau TXT (eksport Google Docs).

## Ringkasan
- Tujuan: mengimpor banyak tugas ke Taiga Sprint tanpa entri satu per satu.
- Input utama: dokumen berformat PDF/TXT yang diekstraksi menjadi data tugas dengan struktur Talent → Note → Estimation.
- Keamanan: patuh ISO (audit trail, akses terbatas, logging insiden; minimisasi data sensitif; prinsip least privilege).
- Kolom wajib di dokumen (setelah ekstraksi): Talent (penugas), Note (judul tugas), Estimation (perkiraan usaha).
- Informasi: User Stories disetel kosong (placeholder jika diperlukan API Taiga mengharuskan field tersebut).

## Alur Bisnis (Ringkas)
1. Pengguna mengotorisasi diri ke impor massal menggunakan token API Taiga.
2. Sistem memilih proyek Taiga; sistem menampilkan daftar sprint (iterasi) yang tersedia.
3. Pengguna memilih sprint yang ada atau membuat sprint baru dengan nama dan tanggal.
4. Pengguna mengunggah dokumen input (PDF atau TXT).
5. Sistem mengektrak data menjadi kolom Talent, Note, Estimation, lalu memvalidasi kolom yang diperlukan.
6. Sistem memetakan Talent ke pengguna Taiga (assignee), Note ke judul tugas, Estimation ke estimasi.
7. Sistem membuat tugas dalam sprint yang dipilih; tidak mengaitkan ke User Stories (sesuai 5.4).
8. Sistem mengembalikan laporan ringkas dan log audit.

## Taiga Self-Hosted
- Implementasi ini mendukung Taiga self-hosted. Set taiga_url ke root API Taiga self-hosted Anda (misalnya https://taiga.yourdomain/api/v1).
- Pastikan token API memiliki hak akses yang cukup (least privilege) dan tidak tersimpan dalam kode sumber.
- Perhatikan bahwa endpoint, autentikasi, dan struktur data mengikuti API Taiga versi self-hosted yang Anda gunakan.

## Peringatan Input PDF
- Model ini tidak bisa membaca file PDF langsung. Jika Anda meng-upload meeting-format.pdf, lakukan ekstraksi teks terlebih dahulu sehingga parsing dapat dilakukan terhadap kolom Talent, Note, Estimation.
- Contoh pesan error yang bisa muncul: ERROR: Cannot read "meeting-format.pdf" (this model does not support pdf input). Inform the user.
- Rekomendasi UX: jika input format = pdf, tampilkan notifikasi untuk konversi ke TXT atau gunakan layanan ekstraksi teks sebelum parsing.
- Implementasi ini mendukung Taiga self-hosted. Set taiga_url ke root API Taiga self-hosted Anda (misalnya https://taiga.yourdomain/api/v1).
- Pastikan token API memiliki hak akses yang cukup (least privilege) dan tidak tersimpan dalam kode sumber.
- Perhatikan bahwa endpoint, autentikasi, dan struktur data mengikuti API Taiga versi self-hosted yang Anda gunakan.

## Struktur Input Dokumen
- Format input: PDF atau TXT (ekstraksi dari Google Docs).
- Dokumen harus memuat data tugas yang dapat dipetakan ke tiga kolom inti:
  - Talent: nama akun Taiga yang menjadi penugasan (assignee)
  - Note: judul tugas
  - Estimation: estimasi waktu/usaha
- Karena model tidak dapat membaca PDF langsung, dokumen PDF harus diekstraksi ke teks terlebih dahulu (mis. TXT) sebelum diparse.
- Contoh skema parsing: satu entri tugas dapat direpresentasikan dalam blok teks berikut (format bebas asalkan dapat diparse menjadi tiga kolom):
  Talent: John Doe
  Note: Implement login feature
  Estimation: 4h

  Talent: Jane Smith
  Note: Create user profile page
  Estimation: 6h

Catatan: jika dokumen tidak mengikuti pola ini, baris yang tidak terpasar akan muncul di failed_rows pada output.

## Struktur Output
- created_tasks: jumlah tugas yang berhasil dibuat.
- failed_rows: daftar baris yang gagal beserta detail kesalahan (baris input yang gagal, alasan kegagalan).
- audit_log: catatan audit dengan timestamp, pengguna, aksi, dan hasil pemetaan.

## Mapping ke Taiga
- Talent → assignee pada Taiga (orang yang ditugaskan).
- Note → judul tugas di Taiga.
- Estimation → estimasi waktu/usaha pada tugas Taiga.
- User Stories tidak terkait (placeholder jika API Taiga mengharuskan field tersebut; lihat 5.4).

## Validasi & Error Handling
- Validasi kehadiran kolom Talent, Note, Estimation.
- Validasi bahwa Talent benar-benar cocok dengan akun pengguna Taiga.
- Jika dokumen adalah PDF, berikan panduan konversi ke TXT/eksraksi teks sebelum parsing.
- Deteksi kegagalan parsing per entri dan tambahkan ke failed_rows dengan detail kesalahan.

## Contoh Dokumen TXT (Extraction Friendly)
Talent: John Doe
Note: Implement authentication flow
Estimation: 3h

Talent: Alice Chen
Note: Design dashboard header
Estimation: 5h

Anda bisa menyimpan contoh ini sebagai .txt dan mengunggahnya melalui UI/API sesuai alur.

## Catatan Teknis Keamanan (ISO 27001)
- Audit trail selalu aktif untuk semua operasi impor.
- Akses token Taiga bersifat least privilege; token tidak disimpan di kode sumber.
- Data sensitif diminimalkan penyimpanannya; enkripsi saat istirahat.
- Log insiden dan perubahan disimpan untuk kepatuhan.

## Implementasi Teknis (Ringkas)
- Input YAML tetap menggunakan doc_input dengan path dan format.
- Proses parser harus bisa membaca TXT hasil ekstraksi, lalu memetakan tiga kolom inti.
- Jika diperlukan, sediakan fallback konversi PDF ke TXT melalui layanan eksternal.

## Pertanyaan Konfirmasi
- Mapping Talent → assignee, Note → judul, Estimation → estimasi sudah benar?
- Apakah dokumen input selalu dalam format TXT setelah ekstraksi, atau perlu dukungan CSV juga?
- Mau saya sertakan contoh file TXT lengkap dengan beberapa entri sebagai referensi?

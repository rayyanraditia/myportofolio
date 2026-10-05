Nama : Rayyan Raditia Pramana

NPM : 2506598955

Kelas : PBP F


### Tugas 1
Ya, saya menggunakan AI, lebih tepatnya Claude AI. Penjelasan lebih lanjutnya dijelaskan pada nomor 2
1. Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti <section>, <article>, atau <aside>? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat static web? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda? Ya, saya menggunakana elemen semantik html 5 seperti <section> dimana hal tersebut digunakan untuk membuat section baru berupa skills section, selain itu saya juga menambahkan <h2> dan <p> dimana hal tersebut berguna untuk membuat bagian dari skills yang ingin saya masukkan seperti soft skills, hard skills, dan languages.

2. Ketika Anda mengatur CSS Anda agar tetap responsive, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile? Tantangan yang paling saya temukan adalah penggunaan CSS dimana hal ini lebih complicated dibandingkan htmlnya sendiri, dalam pengerjaan saya mengerjakan css saya dibantu menggunakan Claude AI. Dalam prosessnya saya merevisi berkali kali dalam html saya dikarenakan elemen ini nantinya akan digunakan dalam css, karena hal ini pula penggunaan AI sangat membantu saya yang tidak memiliki pengalaman dalam css. Terkait kode css saya seharusnya di mobile sudah baik juga mengingat sudah diberikan minmax dan autofit pada bagian skillsnya untuk menyesuakainnya untuk platform mobile

3. Website yang Anda buat saat ini adalah static web murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya? Pada proyek berikutnya saya berharap dapat menggunakan css dengan lebih baik lagi seperti css yang lebih interaktif seperti website wbsite professional lainnya.


### Tugas 2
Penggunaan AI digunakan terutama untuk 3 hal besar, yakni review terkait setiap perubahan yang telah saya lakukan, dimana jika saya menambahkan perubahan besar maka secara rutin sebelum commit saya akan meminta AI untuk review terlebih dahulu, selanjutnya saya menggunakannya untuk membantu pembuatan CSS yang masih belum saya parahmi dan yang terakhir dalam pembuatan testing.
1. Jelaskan alur yang terjadi ketika pengguna membuka halaman portofolio baru, mulai dari permintaan yang diterima proyek hingga data ditampilkan pada browser. Dalam jawabanmu, jelaskan peran urls.py proyek, urls.py aplikasi, view, model, dan template.
Ketika pengguna membuka halaman Education, browser mengirim permintaan ke alamat /education/. urls.py proyek meneruskan permintaan ke urls.py aplikasi main. URL aplikasi kemudian memilih view show_education. View mengambil data dari database melalui model Education, lalu memasukkannya ke dalam context dengan nama education_list. Template education.html menggunakan data tersebut untuk menyusun daftar pendidikan. Django mengirimkan HTML yang sudah dihasilkan ke browser untuk ditampilkan.

2. Mengapa data untuk bagian portofolio baru sebaiknya disimpan pada model dan tidak ditulis langsung di dalam template? Jelaskan dampaknya terhadap kemudahan pemeliharaan dan pengembangan aplikasi.
Data sebaiknya disimpan melalui model agar isi data terpisah dari tampilan halaman. Misalnya, ketika ingin menambahkan riwayat pendidikan, kita cukup menambahkan data ke database tanpa mengedit HTML. Pemeliharaan menjadi lebih mudah karena struktur data diatur oleh model, sedangkan desain diatur melalui template dan CSS. Data yang sama juga dapat digunakan kembali untuk fitur lain, seperti pencarian, penyaringan, atau halaman detail.

3. Apa perbedaan fungsi makemigrations dan migrate pada Django? Berikan contoh perubahan model yang mengharuskanmu menjalankan kedua perintah tersebut.
makemigrations membuat file yang mencatat perubahan struktur model, sedangkan migrate menerapkan perubahan tersebut ke database. Contohnya, ketika menambahkan field study_program pada model Education, jalankan:
python manage.py makemigrations main
python manage.py migrate
Perintah pertama menghasilkan file migrasi untuk penambahan field tersebut. Perintah kedua menjalankan migrasinya sehingga kolom study_program ditambahkan pada tabel Education di database.


### Tugas 3
Saya menggunakan OpenAI Codex sebagai pendamping belajar dan peninjau kode dalam pengerjaan Tugas 3. AI membantu menjelaskan persyaratan, memberikan contoh implementasi, serta meninjau form, view, routing, template, dan CSS yang saya terapkan Pengerjaan dilakukan bertahap. saya meminta penjelasan untuk satu bagian, menerapkan perubahan pada proyek, kemudian meminta review sebelum melanjutkan.
melanjutkan. 
1. Apa manfaat ModelForm dan CSRF token pada form Django?
ModelForm mempermudah pembuatan form berdasarkan model tanpa perlu menulis ulang setiap field dan validasinya. Pada proyek ini, EducationForm digunakan untuk menambah dan mengedit data Education. CSRF token berfungsi melindungi form dari permintaan palsu yang berasal dari situs lain. Token ini ditambahkan menggunakan {% csrf_token %} pada form POST.

2. Mengapa JSON sering dipilih untuk pertukaran data web?
JSON sering digunakan karena formatnya sederhana, ringan, dan mudah dibaca. JSON juga mudah digunakan oleh JavaScript melalui JSON.parse() dan JSON.stringify(), sehingga mempermudah pertukaran data antara backend dan frontend.

3. Bagaimana data Education dikembalikan sebagai JSON?
Saat /api/education/ diakses, Django menjalankan fungsi get_education_json yang mengambil seluruh data menggunakan Education.objects.all(). Data tersebut diubah menjadi JSON menggunakan serializers.serialize() dan dikirim melalui HttpResponse dengan tipe application/json. Pada halaman /education/, fungsi show_education memanggil fungsi tersebut secara langsung, mengubah kembali JSON menjadi objek Education, lalu menampilkannya melalui education.html. Proses ini dilakukan di server tanpa permintaan HTTP tambahan.


### Tugas 4

Tugas ini melanjutkan fitur Education dari Tugas 3 dengan menambahkan authentication, authorization, session, cookie, dan star. Education serta API JSON tetap dapat dibaca tanpa login.

-> Hak Akses
1. Pengunjung: hanya membaca.
2. User: membaca dan star/unstar.
3. Editor: membaca, star/unstar, dan edit.
4. Superuser: seluruh akses.

Pengguna tanpa login diarahkan ke login, sedangkan pengguna tanpa izin mendapat HTTP 403. Hapus dan star/unstar hanya menerima POST.

-> Menjalankan Proyek
python -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Grup Editor dibuat melalui /admin dan pengguna ditambahkan ke grup tersebut.

-> Implementasi
Education memiliki relasi starred_by ke User. Star/unstar dilindungi oleh login, POST, dan CSRF. API menampilkan username pemberi star tanpa mengekspos email atau password. Session digunakan untuk autentikasi, sedangkan cookie `last_login` disimpan setelah login dan dihapus saat logout.

-> Verifikasi
bash
python manage.py check
python manage.py makemigrations --check --dry-run

Pengujian mencakup hak akses, star/unstar, CSRF, redirect login, dan API.

-> Penggunaan AI
Saya menggunakan OpenAI Codex untuk membantu memahami requirement, memberi arahan implementasi, melakukan review, dan pengujian. Implementasi kode tetap dilakukan oleh saya. Berikut adalah beberapa ringkasan prompt yang diberikan:
1. Review implementasi star/unstar pada Education dan cek apakah sudah menggunakan login_required, POST, dan CSRF dengan benar
2. Bantu cek apakah pembatasan tambah, edit, dan hapus Education sudah sesuai dengan hak akses tiap role.


### Tugas 3
1. Jelaskan apa itu debouncing dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX!
    Debouncing adalah teknik menunda pemanggilan fungsi sampai pengguna berhenti memberikan input selama waktu tertentu. Pada pencarian Education, timer 300 milidetik diulang setiap kali pengguna mengetik. Permintaan baru dikirim setelah timer selesai. Teknik ini mengurangi permintaan yang tidak diperlukan ke server karena pencarian tidak dijalankan untuk setiap huruf. Pada implementasi saya, AbortController juga digunakan untuk membatalkan request sebelumnya agar respons lama tidak menimpa hasil pencarian terbaru.

2. Jelaskan fungsi dari penggunaan await ketika kita menggunakan fetch()! Apa yang akan terjadi jika kita tidak menggunakan await?
    fetch() mengembalikan Promise. Penggunaan await menunggu Promise tersebut selesai sebelum melanjutkan langkah berikutnya dalam fungsi async, tanpa memblokir seluruh antarmuka browser. Pada proyek ini, await fetch() menghasilkan objek Response, kemudian await response.json() menghasilkan data JSON yang sudah diparsing. Tanpa await atau penanganan Promise menggunakan .then(), variabel masih berisi Promise sehingga belum dapat digunakan sebagai hasil respons. Status HTTP seperti 400 atau 403 tidak otomatis membuat fetch() melempar error. Karena itu, saya juga memeriksa response.ok untuk membedakan respons berhasil dan gagal.

3. Jelaskan apa itu serangan XSS (Cross-Site Scripting) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django!
    XSS adalah serangan ketika input yang tidak tepercaya diperlakukan sebagai kode aktif dan dijalankan oleh browser. Contohnya adalah input berupa tag HTML dengan event handler berbahaya. Template Django menyediakan autoescaping untuk variabel teks secara default. Namun, ketika data dari AJAX dimasukkan melalui innerHTML, perlindungan template tersebut tidak otomatis berlaku. Jadi, AJAX sendiri bukan penyebab XSS; risiko bergantung pada cara JavaScript menampilkan data. Pada proyek ini, teks dari API dimasukkan menggunakan textContent agar tidak ditafsirkan sebagai HTML. EducationForm juga menggunakan strip_tags() untuk membersihkan judul dan deskripsi, lalu menolak input yang kosong setelah dibersihkan. Sanitasi server tetap perlu disertai penanganan output yang aman di browser.

--> Deklarasi Penggunaan AI
    Saya menggunakan OpenAI Codex untuk membantu memahami instruksi Tugas 5, memberikan contoh kode, menjelaskan konsep, meninjau perubahan, menjalankan pengujian, dan menyusun draf jawaban reflektif. Bagian yang dibantu meliputi endpoint JSON Education, pencarian dengan debouncing, rendering melalui AJAX, validasi form, modal tambah, CSRF, perlindungan XSS, dan notifikasi toast. Saya menerapkan perubahan file sendiri berdasarkan arahan melalui chat, kemudian meminta review sebelum melanjutkan.
    Strategi prompt yang saya gunakan umumnya berupa permintaan pengujian terhadap fitur yang telah diletakan dalam kode saya seperti "Sesuaikan kode saya dengan instruksi yang sudah diberikan, apakah perubahan yang telah dilakukan sudah benar atau belum? jika belum sesuai maka beri tahu secara jelas saya salah dimana dan harusnya seperti apa?"
    Saya tetap memeriksa saran AI melalui pengujian. Review kode tidak selalu membuktikan perilaku di browser, sehingga pengujian backend dan browser dilakukan secara terpisah. Saya juga memperbaiki kode lama yang tertinggal setelah return, import duplikat, serta whitespace berdasarkan hasil review.

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

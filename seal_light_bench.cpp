// Lightweight standalone bench harness for NINE65-augmented SEAL.
// Measures a few representative ops for BFV and CKKS using std::chrono.

#include <seal/seal.h>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

using namespace seal;
using Clock = std::chrono::high_resolution_clock;

struct BenchResult {
    std::string name;
    double ms;
};

template <typename Fn>
double time_op(size_t iters, Fn&& fn)
{
    auto start = Clock::now();
    for (size_t i = 0; i < iters; ++i) {
        fn();
    }
    auto end = Clock::now();
    std::chrono::duration<double, std::milli> diff = end - start;
    return diff.count() / static_cast<double>(iters);
}

void print_result(const BenchResult& r)
{
    std::cout << std::left << std::setw(28) << r.name << std::right << std::setw(10)
              << std::fixed << std::setprecision(3) << r.ms << " ms\n";
}

std::vector<BenchResult> bench_bfv()
{
    std::vector<BenchResult> out;

    EncryptionParameters parms(scheme_type::bfv);
    size_t poly_degree = 4096;
    parms.set_poly_modulus_degree(poly_degree);
    parms.set_coeff_modulus(CoeffModulus::BFVDefault(poly_degree));
    parms.set_plain_modulus(PlainModulus::Batching(poly_degree, 20));

    auto context = SEALContext(parms, true, sec_level_type::none);
    KeyGenerator keygen(context);
    auto sk = keygen.secret_key();
    PublicKey pk;
    keygen.create_public_key(pk);
    RelinKeys relin;
    keygen.create_relin_keys(relin);

    BatchEncoder encoder(context);
    Encryptor encryptor(context, pk);
    Decryptor decryptor(context, sk);
    Evaluator evaluator(context);

    size_t slots = encoder.slot_count();
    std::vector<uint64_t> vec(slots, 7);
    Plaintext plain;
    encoder.encode(vec, plain);

    Ciphertext c1, c2;
    encryptor.encrypt(plain, c1);
    encryptor.encrypt(plain, c2);

    constexpr size_t iters = 5;

    out.push_back({"BFV Encrypt", time_op(iters, [&] {
        Ciphertext tmp;
        encryptor.encrypt(plain, tmp);
    })});

    out.push_back({"BFV Decrypt", time_op(iters, [&] {
        Plaintext tmp;
        decryptor.decrypt(c1, tmp);
    })});

    out.push_back({"BFV Add ct+ct", time_op(iters, [&] {
        Ciphertext tmp;
        evaluator.add(c1, c2, tmp);
    })});

    out.push_back({"BFV Mul ct*ct", time_op(iters, [&] {
        Ciphertext tmp;
        evaluator.multiply(c1, c2, tmp);
        evaluator.relinearize_inplace(tmp, relin);
    })});

    return out;
}

std::vector<BenchResult> bench_ckks()
{
    std::vector<BenchResult> out;

    EncryptionParameters parms(scheme_type::ckks);
    size_t poly_degree = 4096;
    parms.set_poly_modulus_degree(poly_degree);
    parms.set_coeff_modulus(CoeffModulus::Create(poly_degree, {60, 40, 40, 60}));

    auto context = SEALContext(parms, true, sec_level_type::none);
    KeyGenerator keygen(context);
    auto sk = keygen.secret_key();
    PublicKey pk;
    keygen.create_public_key(pk);
    RelinKeys relin;
    keygen.create_relin_keys(relin);

    CKKSEncoder encoder(context);
    Encryptor encryptor(context, pk);
    Decryptor decryptor(context, sk);
    Evaluator evaluator(context);

    double scale = pow(2.0, 40);
    std::vector<double> data(encoder.slot_count(), 1.5);
    Plaintext plain;
    encoder.encode(data, scale, plain);

    Ciphertext c1, c2;
    encryptor.encrypt(plain, c1);
    encryptor.encrypt(plain, c2);

    constexpr size_t iters = 5;

    out.push_back({"CKKS Encrypt", time_op(iters, [&] {
        Ciphertext tmp;
        encryptor.encrypt(plain, tmp);
    })});

    out.push_back({"CKKS Decrypt", time_op(iters, [&] {
        Plaintext tmp;
        decryptor.decrypt(c1, tmp);
    })});

    out.push_back({"CKKS Add ct+ct", time_op(iters, [&] {
        Ciphertext tmp;
        evaluator.add(c1, c2, tmp);
    })});

    out.push_back({"CKKS Mul ct*ct", time_op(iters, [&] {
        Ciphertext tmp;
        evaluator.multiply(c1, c2, tmp);
        evaluator.relinearize_inplace(tmp, relin);
        evaluator.rescale_to_next_inplace(tmp);
    })});

    return out;
}

int main()
{
    try {
        std::cout << "NINE65 + SEAL Lightweight Bench (approximate, wall-clock)\n";
        std::cout << "-------------------------------------------------------\n\n";

        auto bfv = bench_bfv();
        auto ckks = bench_ckks();

        std::cout << "[BFV]\n";
        for (const auto& r : bfv) {
            print_result(r);
        }
        std::cout << "\n[CKKS]\n";
        for (const auto& r : ckks) {
            print_result(r);
        }
    } catch (const std::exception& e) {
        std::cerr << "Bench failed: " << e.what() << '\n';
        return 1;
    }

    return 0;
}

"""
Seed script — 5 örnek startup analizi oluşturur.

Kullanım:
    cd api
    python seed_data.py

Demo kullanıcısı (seed@example.com / Seed12345) yoksa oluşturulur,
varsa o kullanıcının altına 5 örnek Idea kaydı eklenir.
"""

import asyncio

from sqlalchemy.future import select

from src.lib.db.database import SessionLocal, engine, Base
from src.lib.db.models.user import User
from src.lib.db.models.idea import Idea
from src.lib.db.models.chat import Chat  # noqa: F401 — tablo oluşması için import gerekli
from src.lib.utils.security import get_password_hash
from src.controllers.idea_controller import calculate_score


SEED_EMAIL = "seed@example.com"
SEED_PASSWORD = "Seed12345"
SEED_FULLNAME = "Seed Demo"

SAMPLE_IDEAS = [
    {
        "title": "Yapay Zeka Destekli Diyetisyen",
        "executive_summary": "Kullanıcı sağlık verilerine göre kişiselleştirilmiş günlük menü öneren mobil uygulama.",
        "problem_statement": "Bireysel diyet planları pahalı ve erişilmesi zor.",
        "target_audience": "20-45 yaş arası sağlıklı yaşam ilgilileri.",
        "value_proposition": "Diyetisyen ücretinin %10'una otomatik, dinamik plan.",
        "swot_analysis": {
            "strengths": ["Düşük operasyon maliyeti", "Kişiselleştirme"],
            "weaknesses": ["Sağlık verisi güveni"],
            "opportunities": ["Sağlık trendi", "Mobil pazar büyümesi", "B2B kurumsal sağlık"],
            "threats": ["Regülasyon", "Mevcut diyet uygulamaları"],
        },
        "market_analysis": {
            "market_size": "Türkiye'de dijital sağlık pazarı 1.2 milyar USD ve hızla büyüyor.",
            "competitors": ["Yazio", "Fitatu", "Diyetkolik"],
            "trends": "Kişiselleştirilmiş beslenme, AI tabanlı öneri sistemleri.",
        },
        "business_model": "Freemium abonelik + kurumsal lisans.",
    },
    {
        "title": "Mahalle Esnafı için Hızlı Teslimat Ağı",
        "executive_summary": "Mahalle bakkalları için 30 dk içi teslimat sağlayan kurye paylaşım platformu.",
        "problem_statement": "Bakkallar büyük platformların yüksek komisyonlarını ödeyemiyor.",
        "target_audience": "Mahalle bakkalları, küçük marketler, kasaplar.",
        "value_proposition": "Komisyon yerine sabit aylık ücret + paylaşımlı kurye havuzu.",
        "swot_analysis": {
            "strengths": ["Düşük komisyon modeli", "Yerel ağ etkisi"],
            "weaknesses": ["Lojistik karmaşıklığı", "Düşük başlangıç ölçeği"],
            "opportunities": ["Hyperlocal commerce trendi", "Kurye paylaşım ekonomisi"],
            "threats": ["Getir, Migros Hemen gibi büyük oyuncular"],
        },
        "market_analysis": {
            "market_size": "Türkiye q-commerce pazarı yıllık 800 milyon USD ve büyüyor.",
            "competitors": ["Getir", "Migros Hemen", "Banabi"],
            "trends": "10 dakika teslimat, hyperlocal modeller.",
        },
        "business_model": "Esnaftan aylık abonelik + kurye başına ücret.",
    },
    {
        "title": "KOBİ'ler için Otomatik Vergi Asistanı",
        "executive_summary": "Muhasebe yazılımı entegrasyonu ile KDV/Stopaj beyannamelerini otomatik hazırlayan SaaS.",
        "problem_statement": "Küçük işletmeler vergi süreçlerinde mali müşavire bağımlı ve hata oranı yüksek.",
        "target_audience": "Yıllık cirosu 5M TL altı KOBİ'ler.",
        "value_proposition": "Aylık 299 TL'ye otomatik beyanname taslağı + uyarı sistemi.",
        "swot_analysis": {
            "strengths": ["Tekrarlayan gelir", "Yüksek müşteri tutma"],
            "weaknesses": ["Mevzuat değişikliklerine bağımlılık"],
            "opportunities": ["e-Dönüşüm zorunlulukları", "Dijitalleşen KOBİ'ler"],
            "threats": ["Logo, Mikro gibi yerleşik oyuncular", "Mali müşavir lobisi"],
        },
        "market_analysis": {
            "market_size": "Türkiye'de 3.2 milyon aktif KOBİ var; SaaS penetrasyonu %15.",
            "competitors": ["Paraşüt", "Bizmu", "Logo İşbaşı"],
            "trends": "e-Fatura zorunluluğu, KOBİ dijitalleşmesi.",
        },
        "business_model": "Aylık SaaS abonelik (3 kademe).",
    },
    {
        "title": "Çocuklar için Kodlama Oyun Platformu",
        "executive_summary": "7-14 yaş çocukların oyunlaştırma ile kodlama öğrendiği web platformu.",
        "problem_statement": "Çocuklar için kodlama eğitimi pahalı ve sıkıcı.",
        "target_audience": "Veliler ve özel okullar.",
        "value_proposition": "Aylık 99 TL'ye sınırsız ders + sertifika.",
        "swot_analysis": {
            "strengths": ["Düşük müşteri edinme maliyeti (okul kanalı)", "Oyun mekaniği"],
            "weaknesses": ["İçerik üretim maliyeti yüksek"],
            "opportunities": ["MEB STEM müfredatı", "Yurtdışı pazar"],
            "threats": ["Code.org gibi ücretsiz alternatifler"],
        },
        "market_analysis": {
            "market_size": "Çocuk EdTech pazarı global 12 milyar USD.",
            "competitors": ["Codemonkey", "Kodluyoruz Junior", "Tinkercad"],
            "trends": "Gamification, AI tutor, sertifikasyon.",
        },
        "business_model": "B2C abonelik + B2B okul lisansı.",
    },
    {
        "title": "Yerel Üretici Sebze Meyve Pazarı",
        "executive_summary": "Çiftçiden tüketiciye doğrudan organik ürün satışı yapan platform.",
        "problem_statement": "Çiftçi az kazanıyor, tüketici taze ürüne ulaşamıyor; aradaki marj aracılarda.",
        "target_audience": "Şehirli orta-üst gelir grubu, organik ürün tüketicileri.",
        "value_proposition": "Aracısız %30 daha taze, %20 daha ucuz organik ürün.",
        "swot_analysis": {
            "strengths": ["Üretici ile direkt ilişki", "Taze ürün"],
            "weaknesses": ["Lojistik soğuk zincir", "Mevsimsellik"],
            "opportunities": ["Organik trendi", "Sürdürülebilirlik bilinci"],
            "threats": ["Migros Sanal, Çiçeksepeti Gurme", "Mevsim dışı ürün eksikliği"],
        },
        "market_analysis": {
            "market_size": "Türkiye organik gıda pazarı 1 milyar USD ve %15 büyüyor.",
            "competitors": ["Tazedirekt", "Çiçeksepeti Gurme", "Yerel pazarlar"],
            "trends": "Farm-to-table, kısa tedarik zinciri.",
        },
        "business_model": "Sipariş başına %15 komisyon + premium üyelik.",
    },
]


async def ensure_demo_user(db) -> User:
    result = await db.execute(select(User).where(User.email == SEED_EMAIL))
    user = result.scalars().first()
    if user:
        return user

    user = User(
        fullname=SEED_FULLNAME,
        email=SEED_EMAIL,
        password_hash=get_password_hash(SEED_PASSWORD),
        country="Türkiye",
        city="İstanbul",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        user = await ensure_demo_user(db)

        existing = await db.execute(select(Idea).where(Idea.user_id == user.id))
        if existing.scalars().first():
            print(f"Demo user {SEED_EMAIL} already has ideas — skipping seed.")
            return

        for sample in SAMPLE_IDEAS:
            idea = Idea(
                user_id=user.id,
                title=sample["title"],
                executive_summary=sample["executive_summary"],
                problem_statement=sample["problem_statement"],
                target_audience=sample["target_audience"],
                value_proposition=sample["value_proposition"],
                swot_analysis=sample["swot_analysis"],
                market_analysis=sample["market_analysis"],
                business_model=sample["business_model"],
                score=calculate_score(sample),
            )
            db.add(idea)

        await db.commit()
        print(f"Inserted {len(SAMPLE_IDEAS)} sample ideas for {SEED_EMAIL}.")
        print(f"Login: {SEED_EMAIL} / {SEED_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())

export enum Currency {
    US_Dollar = "USD",
    Euro = "EUR",
    UK_Pound = "GBP",
    Turkish_Lira = "TRY",
}

export enum WorkplaceType {
    OnSite = 1,
    Remote = 2,
    Hybrid = 3,
}
    

export enum ExperienceLevel {
    Entry = 1,
    Mid = 2,
    Senior = 3,
    Executive = 4,
}

export interface JobListing {
    _id: string,

    ext_id: string,
    title: string,
    company: string,
    source_url: string,

    date_posted: Date,
    date_created: Date,

    salary_currency: Currency
    min_salary_monthly?: number,
    max_salary_monthly?: number,

    location: string,
    workplace_type: WorkplaceType,

    expected_experience?: ExperienceLevel,
    min_experience_years?: number,
    max_experience_years?: number,

    expected_skills: string[],

    description: string,
}
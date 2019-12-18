# NUT Dataset Annotation Guidelines

For future research, we provide the annotations guidelines that we distributed to our annotators to mark PHI examples in the NUT corpus. Those guidelines can be found below.

## Annotation Guidelines

For the development of an automatic de-identification software, we require medical records where the protected health information (PHI) has been marked up so that the annotations can be used to develop automatic de-identification methods.
The annotated data is the type information that must be removed/replaced from a patient record in order to be considered de-identified.
We defined 8 categories of PHI that can relate to a patient, but also to relatives, employers, household members or the doctor of a patient.
In total 16 tags can be assigned to a piece of text:


   * NAME
      - Name
      - Initials
   * PROFESSION (not of medical staff)
   * LOCATION
      - Hospital
      - Care Institute (Zorgorganisatie)
      - Organization/Company
      - Address
      - Internal location (e.g., building code, room, floor)
   * AGE
   * DATE
   * CONTACT
      - Phone/FAX
      - Email
      - URL/IP-address
   * ID
      - Social security number (SSN/BSN)
      - Any other ID number
   * OTHER

### Overall Principles

When annotating, the following rules apply:

   1. When tagging something that is PHI but it is not obvious what to tag it as, think about what it should be replaced with and whether that will make sense in the document ("replacement test").
   1. When in doubt whether something is `tag A` or `tag B`, annotate it as the most likely tag and add a note to the annotation.
   1. When in doubt, annotate! We do not want to miss PHI.

To give an example of the replacement test, consider this sentence:

```
In 2015 is hij met de andere cliënten verhuisd naar de
woonvoorziening Kerklaan in Bennebroek.

[Translated] In 2015 he moved with other clients to the
woonvoorziening Kerklaan in Bennebroek.
```

It is clear that the housing facility (Dutch: woonvoorziening) has been named after its location "Kerklaan." So instead of
annotating "Kerklaan" as an address, "woonvoorziening Kerklaan" should be annotated as care
institute, as we would replace this with the name of another care institute. The final annotation
should look like this:

```xml
In <DATE 2015> is hij met de andere cliënten verhuisd naar de
<CARE-INSTITUTE woonvoorziening Kerklaan> in <ADDRESS Bennebroek>.

[Translated] In <DATE 2015> he moved with other clients to the
<CARE-INSTITUTE Kerklaan> in <ADDRESS Bennebroek>.
```

### Example Annotations per Category

The table below provides example annotations for each of the PHI categories that were distributed to each annotator alongside with the instructions.

| Category | Examples | Exclude from Annotation |
|-------------------|-----------------------------------------------------------------------------------------|-------------------------------------|
| Name | "Bart van der Boor", "Boor, van der", "B. Boor", "Anne FP Jansen" | Titles (Dhr., Mw., Dr., etc.) |
| Initials | J.F., JF. | Titles (see above) |
| Profession | "stratenmaker", "programmeur", "militaire dienst" | Professions of medical staff |
| Hospital | "Universitair Medisch Centrum", "UMC" |  |
| Care Institute | "Cromhoff", "Mgr. Bekkershuis" |  |
| Organization | "Ikea", "de Vink", "de Efteling" | Generic names: "bouwmarkt" |
| Address | "Van Meeuwenstraat 2, 1234AB Town", "Den Bosch", "Nieuw-Zeeland" |  |
| Internal Location | "8.1" | Generic locations: "surgery room" |
| Age | "2 jaar en 4 maanden", "78" |  |
| Date | "15-02-19", "2019", "vrijdag", "Zomer '02", "herfstvakantie", "koningsdag", | Time of day (14:27) |
| ID | IBAN, license plate, employee number |  |
| SSN/BSN | Burgerservicenummer (BSN) |  |

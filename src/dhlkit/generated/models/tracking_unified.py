# Generated from an official DHL OpenAPI document. DO NOT EDIT.

from __future__ import annotations

from typing import Annotated, Literal

from dhlkit.models import DhlModel
from pydantic import AnyUrl, Field, RootModel


class Service(
    RootModel[
        Literal[
            'dgf',
            'dsc',
            'ecommerce',
            'ecommerce-apac',
            'ecommerce-europe',
            'ecommerce-ppl',
            'ecommerce-iberia',
            'express',
            'freight',
            'parcel-de',
            'parcel-nl',
            'parcel-pl',
            'parcel-uk',
            'post-de',
            'post-international',
            'sameday',
            'svb',
        ]
    ]
):
    root: Annotated[
        Literal[
            'dgf',
            'dsc',
            'ecommerce',
            'ecommerce-apac',
            'ecommerce-europe',
            'ecommerce-ppl',
            'ecommerce-iberia',
            'express',
            'freight',
            'parcel-de',
            'parcel-nl',
            'parcel-pl',
            'parcel-uk',
            'post-de',
            'post-international',
            'sameday',
            'svb',
        ],
        Field(
            description='Service (provider) used to resolve this tracking number (id)',
            examples=['express'],
        ),
    ]


class Ttl(RootModel[int]):
    root: Annotated[
        int,
        Field(
            description='Define the TTL value in seconds of shipment between 30 and 365 days',
            ge=2592000,
            le=31536000,
        ),
    ] = 15552000


class SecretPolicy(RootModel[Literal['none', 'postal-code']]):
    root: Annotated[
        Literal['none', 'postal-code'],
        Field(
            description='A secret policy protecting sensitive information',
            examples=['postal-code'],
        ),
    ] = 'postal-code'


class CountryCode(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description='Code specifying the country using ISO 3166-1 alpha-2',
            examples=['CZ'],
        ),
    ]


class SecuredAddress(DhlModel):
    field_policy: Annotated[
        SecretPolicy | None, Field(alias='@policy', validate_default=True)
    ] = 'postal-code'
    address_locality: Annotated[
        str | None,
        Field(
            alias='addressLocality',
            description='Text specifying the name of the locality, for example a city',
            examples=['Prague'],
        ),
    ] = None
    address_locality_servicing: Annotated[
        str | None,
        Field(
            alias='addressLocalityServicing',
            description='Text specifying a detail of address locality',
            examples=['Chodov'],
        ),
    ] = None
    address_region: Annotated[
        str | None,
        Field(
            alias='addressRegion',
            description='Text specifying a detail of country',
            examples=['Prague 11'],
        ),
    ] = None
    country_code: Annotated[CountryCode | None, Field(alias='countryCode')] = None
    postal_code: Annotated[
        str | None,
        Field(
            alias='postalCode',
            description='Text specifying the postal code for an address',
            examples=['14000'],
        ),
    ] = None
    street_address: Annotated[
        str | None,
        Field(
            alias='streetAddress',
            description='The street address expressed as free form text',
            examples=['Batman Avenue 1040'],
        ),
    ] = None
    address_line: Annotated[
        str | None,
        Field(
            alias='addressLine',
            description='Text specifying the addressLine, for example an apartment, suite, or floor number',
            examples=['3rd Floor'],
        ),
    ] = None


class ServicePoint(DhlModel):
    url: str | None = None
    label: str | None = None


class SecuredPlace(DhlModel):
    address: SecuredAddress | None = None
    service_point: Annotated[ServicePoint | None, Field(alias='servicePoint')] = None


class StatusCode(
    RootModel[Literal['delivered', 'failure', 'pre-transit', 'transit', 'unknown']]
):
    root: Annotated[
        Literal['delivered', 'failure', 'pre-transit', 'transit', 'unknown'],
        Field(
            description='Code of the status (high-level grouping statuses)',
            examples=['delivered'],
        ),
    ]


class EstimatedDeliveryTimeFrame(DhlModel):
    estimated_from: Annotated[
        str | None,
        Field(
            alias='estimatedFrom',
            description='The start date of the estimated time frame',
        ),
    ] = None
    estimated_through: Annotated[
        str | None,
        Field(
            alias='estimatedThrough',
            description='The end date of the estimated time frame',
        ),
    ] = None


class ReturnFlag(RootModel[bool]):
    root: Annotated[
        bool,
        Field(description='A flag whether the delivery is returned back to consignor'),
    ] = False


class Product(DhlModel):
    delivery_method_remark: Annotated[
        str | None,
        Field(
            alias='deliveryMethodRemark',
            description='Specific detail of product',
            examples=['D2P'],
        ),
    ] = None
    product_code: Annotated[str | None, Field(alias='productCode')] = None
    product_name: Annotated[
        str | None,
        Field(
            alias='productName',
            description='Business unit product or service',
            examples=['Worldwide Priority'],
        ),
    ] = None


class Provider(DhlModel):
    destination_provider: Annotated[
        Literal[
            'acs-courier',
            'anpost',
            'bpost',
            'bring',
            'chronopost',
            'colis-prive',
            'econnect',
            'express',
            'fastway',
            'freight',
            'freight-fr',
            'freight-se',
            'hrvatska-posta',
            'magyar-posta',
            'oepag',
            'parcel-be',
            'parcel-bl',
            'parcel-cz',
            'parcel-de',
            'parcel-es',
            'parcel-iberia',
            'parcel-lu',
            'parcel-nl',
            'parcel-pl',
            'parcel-pt',
            'parcel-uk',
            'posta',
            'posta-slovenije',
            'posti',
            'poste-italiane',
            'ppl',
            'rapido',
            'relais-colis',
            'slovak-parcel-service',
            'speedy',
            'sps',
            'trans-o-flex',
            'urgent-cargus',
        ],
        Field(
            alias='destinationProvider',
            description='The name of the provider organization handling the delivery in the destination country',
        ),
    ]


class UnknownEntity(DhlModel):
    field_type: Annotated[Literal['UnknownEntity'], Field(alias='@type')] = (
        'UnknownEntity'
    )
    field_policy: Annotated[SecretPolicy | None, Field(alias='@policy')] = None
    family_name: Annotated[str | None, Field(alias='familyName')] = None
    given_name: Annotated[str | None, Field(alias='givenName')] = None
    name: str | None = None
    organization_name: Annotated[str | None, Field(alias='organizationName')] = None
    address: SecuredAddress | None = None


class Organization(DhlModel):
    field_type: Annotated[
        Literal['Organization'], Field(alias='@type', examples=['Organization'])
    ] = 'Organization'
    field_policy: Annotated[
        SecretPolicy | None, Field(alias='@policy', validate_default=True)
    ] = 'postal-code'
    name: Annotated[
        str | None,
        Field(description='The name of the person', examples=['Linford Alene']),
    ] = None
    organization_name: Annotated[
        str | None,
        Field(
            alias='organizationName',
            description='The name of organization',
            examples=['Highgate School and Academy'],
        ),
    ] = None
    address: SecuredAddress | None = None


class Company(DhlModel):
    field_type: Annotated[
        Literal['Company'], Field(alias='@type', examples=['Company'])
    ] = 'Company'
    field_policy: Annotated[
        SecretPolicy | None, Field(alias='@policy', validate_default=True)
    ] = 'postal-code'
    name: Annotated[
        str | None,
        Field(description='The name of the person', examples=['Linford Alene']),
    ] = None
    organization_name: Annotated[
        str | None,
        Field(
            alias='organizationName',
            description='The name of organization',
            examples=['The First Dome Ltd.'],
        ),
    ] = None
    address: SecuredAddress | None = None


class Person(DhlModel):
    field_type: Annotated[
        Literal['Person'], Field(alias='@type', examples=['Person'])
    ] = 'Person'
    field_policy: Annotated[
        SecretPolicy | None, Field(alias='@policy', validate_default=True)
    ] = 'postal-code'
    family_name: Annotated[
        str | None,
        Field(alias='familyName', description='Family name, the last name of a person'),
    ] = None
    given_name: Annotated[
        str | None,
        Field(alias='givenName', description='Given name, the first name of a person'),
    ] = None
    name: Annotated[
        str | None,
        Field(description='The name of the person', examples=['Dariel Leola']),
    ] = None
    address: SecuredAddress | None = None


class PersonEntity(RootModel[UnknownEntity | Organization | Company | Person]):
    root: Annotated[
        UnknownEntity | Organization | Company | Person,
        Field(
            description='A real organization or personal entity, if type is not specified, a Organization implementation is used',
            discriminator='field_type',
        ),
    ]


class ProofOfDelivery(DhlModel):
    document_url: Annotated[
        AnyUrl | None,
        Field(
            alias='documentUrl',
            description='The link to related electronic proof of delivery document',
            examples=[
                'https://webpod.dhl.com/pod?token=510f1359603a768a57af49cf10083f90&language=en'
            ],
        ),
    ] = None
    signature_url: Annotated[
        AnyUrl | None,
        Field(
            alias='signatureUrl', description='The link to related electronic signature'
        ),
    ] = None
    signed: PersonEntity | None = None
    timestamp: Annotated[
        str | None,
        Field(
            description='Date and time of related proof of delivery document',
            examples=['2022-10-21T12:30:00'],
        ),
    ] = None


class PieceId(RootModel[str]):
    root: Annotated[
        str, Field(description='Identification of item or piece in the shipment')
    ]


class QuantitativeValue(DhlModel):
    unit_text: Annotated[
        str | None,
        Field(
            alias='unitText',
            description='A string or text indicating the unit of measurement',
            examples=['m'],
        ),
    ] = None
    value: Annotated[
        float | None,
        Field(
            description='The value of the quantitative value or property value node',
            examples=[1.5],
        ),
    ] = None


class Dimensions(DhlModel):
    height: QuantitativeValue | None = None
    length: QuantitativeValue | None = None
    width: QuantitativeValue | None = None


class SecretScope(RootModel[Literal['public', 'secret', 'sensitive']]):
    root: Annotated[
        Literal['public', 'secret', 'sensitive'],
        Field(
            description='A secret scope of protected or sensitive information',
            examples=['public'],
        ),
    ]


class ReferenceType(
    RootModel[
        Literal[
            'container-number',
            'customer-confirmation-number',
            'customer-reference',
            'domestic-consignment-id',
            'ecommerce-number',
            'housebill',
            'local-tracking-number',
            'masterbill',
            'payer-account-number',
            'receiver-account-number',
            'reference',
            'shipment-id',
            'shipper-account-number',
            'routing-code',
            'customer-order-number',
        ]
    ]
):
    root: Annotated[
        Literal[
            'container-number',
            'customer-confirmation-number',
            'customer-reference',
            'domestic-consignment-id',
            'ecommerce-number',
            'housebill',
            'local-tracking-number',
            'masterbill',
            'payer-account-number',
            'receiver-account-number',
            'reference',
            'shipment-id',
            'shipper-account-number',
            'routing-code',
            'customer-order-number',
        ],
        Field(
            description='Type of reference', examples=['customer-confirmation-number']
        ),
    ]


class Reference(DhlModel):
    field_scope: Annotated[SecretScope | None, Field(alias='@scope')] = None
    number: Annotated[str | None, Field(description='A value of reference')] = None
    type: ReferenceType


class ValueAddedService(DhlModel):
    service_type: Annotated[
        Literal[
            'bulky',
            'pickup',
            'gogreen',
            'priority',
            'extraInsurance',
            'directInjection',
            'cashOnDelivery',
            'importFees',
        ]
        | None,
        Field(alias='serviceType'),
    ] = None
    service_criteria: Annotated[str | None, Field(alias='serviceCriteria')] = None
    service_flag: Annotated[bool | None, Field(alias='serviceFlag')] = None


class ControlledDataCode(
    RootModel[
        Literal[
            'consignee-city',
            'servicepoint-facilityId',
            'servicepoint-url',
            'shipper-city',
            'signatory-name',
        ]
    ]
):
    root: Annotated[
        Literal[
            'consignee-city',
            'servicepoint-facilityId',
            'servicepoint-url',
            'shipper-city',
            'signatory-name',
        ],
        Field(examples=['consignee-city']),
    ]


class DgfLocation(DhlModel):
    dgf_location_name: Annotated[
        str | None,
        Field(
            alias='dgf:locationName',
            description='The name of the location',
            examples=['GOTHENBURG'],
        ),
    ] = None


class DgfAirport(DgfLocation):
    dgf_location_code: Annotated[
        str | None,
        Field(
            alias='dgf:locationCode',
            description='Airport of departure/destination in IATA code format',
            examples=['AMS'],
        ),
    ] = None
    country_code: Annotated[CountryCode | None, Field(alias='countryCode')] = None


class DgfRoute(DhlModel):
    dgf_vessel_name: Annotated[
        str | None,
        Field(
            alias='dgf:vesselName',
            description='Vessel Name for Ocean',
            examples=['MAERSK SARAT'],
        ),
    ] = None
    dgf_voyage_flight_number: Annotated[
        str | None,
        Field(
            alias='dgf:voyageFlightNumber',
            description='Voyage number for Ocean, Flight Carrier and Number for Air',
            examples=['TR TRUCK'],
        ),
    ] = None
    dgf_airport_of_departure: Annotated[
        DgfAirport | None, Field(alias='dgf:airportOfDeparture')
    ] = None
    dgf_airport_of_destination: Annotated[
        DgfAirport | None, Field(alias='dgf:airportOfDestination')
    ] = None
    dgf_estimated_departure_date: Annotated[
        str | None,
        Field(
            alias='dgf:estimatedDepartureDate',
            description='Flight Estimated Date and Time of Departure',
        ),
    ] = None
    dgf_estimated_arrival_date: Annotated[
        str | None,
        Field(
            alias='dgf:estimatedArrivalDate',
            description='Flight Estimated Date and Time of Arrival',
        ),
    ] = None
    dgf_place_of_acceptance: Annotated[
        DgfLocation | None, Field(alias='dgf:placeOfAcceptance')
    ] = None
    dgf_port_of_loading: Annotated[
        DgfLocation | None, Field(alias='dgf:portOfLoading')
    ] = None
    dgf_port_of_unloading: Annotated[
        DgfLocation | None, Field(alias='dgf:portOfUnloading')
    ] = None
    dgf_place_of_delivery: Annotated[
        DgfLocation | None, Field(alias='dgf:placeOfDelivery')
    ] = None


class Location(DhlModel):
    lat: Annotated[
        float | None, Field(description='Latitude value', examples=[18.556873])
    ] = None
    lon: Annotated[
        float | None, Field(description='Longitude value', examples=[-70.06104])
    ] = None


class Humidity(DhlModel):
    value: Annotated[str | None, Field(description='Humidity value')] = None
    unit: Annotated[
        Literal['percentage'] | None,
        Field(description='Unit of measurement', examples=['percentage']),
    ] = None
    device_id: Annotated[
        str | None,
        Field(alias='deviceId', description='Sensor device id measured the humidity'),
    ] = None


class Pressure(DhlModel):
    value: Annotated[str | None, Field(description='Pressure value')] = None
    unit: Annotated[
        Literal['pascal', 'bar', 'psi'] | None,
        Field(description='Unit of measurement', examples=['pascal']),
    ] = None
    device_id: Annotated[
        str | None,
        Field(alias='deviceId', description='Sensor device id measured the pressure'),
    ] = None


class Temperature(DhlModel):
    value: Annotated[str | None, Field(description='Temperature value')] = None
    unit: Annotated[
        Literal['celsius', 'fahrenheit', 'kelvin'] | None,
        Field(description='Unit of measurement', examples=['celsius']),
    ] = None
    device_id: Annotated[
        str | None,
        Field(
            alias='deviceId', description='Sensor device id measured the temperature'
        ),
    ] = None


class Tilt(DhlModel):
    value: Annotated[str | None, Field(description='Tilt value')] = None
    unit: Annotated[
        Literal['degree', 'radian'] | None,
        Field(description='Unit of measurement', examples=['degree']),
    ] = None
    device_id: Annotated[
        str | None,
        Field(alias='deviceId', description='Sensor device id measured the tilt'),
    ] = None


class Measurement(DhlModel):
    field_policy: Annotated[
        SecretPolicy | None, Field(alias='@policy', validate_default=True)
    ] = 'postal-code'
    timestamp: Annotated[
        str | None,
        Field(
            description='Date and time when the telemetry data was created by the origin system'
        ),
    ] = None
    device_id: Annotated[
        str | None,
        Field(alias='deviceId', description='Sensor device id measured the humidity'),
    ] = None
    piece_ids: Annotated[
        list[PieceId] | None,
        Field(alias='pieceIds', description='piece ids of shipment'),
    ] = None
    location: Location | None = None
    humidity: Humidity | None = None
    pressure: Pressure | None = None
    temperature: Temperature | None = None
    tilt: Tilt | None = None


class ProblemDetail(DhlModel):
    detail: Annotated[
        str | None,
        Field(
            description='A human-readable explanation specific to this occurrence of the problem',
            examples=['Detailed explanation of problem'],
        ),
    ] = None
    instance: Annotated[
        AnyUrl | None,
        Field(
            description='A URI reference that identifies the specific occurrence of the problem',
            examples=['https://www.some.uri/issue/400'],
        ),
    ] = None
    status: Annotated[
        float | None, Field(description='The HTTP status code', examples=[400])
    ] = None
    title: Annotated[
        str | None,
        Field(
            description='A short, human-readable summary of the problem type',
            examples=['Something already happen'],
        ),
    ] = None
    type: Annotated[
        str | None,
        Field(
            description='An identity of caused exception class',
            examples=['SomeException'],
        ),
    ] = None


class TrackingShipmentStatus(DhlModel):
    timestamp: Annotated[
        str, Field(description='A combination of date and time of day')
    ]
    location: SecuredPlace | None = None
    status_code: Annotated[StatusCode, Field(alias='statusCode')]
    status: Annotated[
        str | None, Field(description='Short description of the status - title')
    ] = None
    status_detailed: Annotated[
        str | None,
        Field(alias='statusDetailed', description='Detailed status of the shipment'),
    ] = None
    description: Annotated[
        str | None, Field(description='Human-readable detailed description')
    ] = None
    remark: Annotated[
        str | None, Field(description='Remark regarding the shipment status')
    ] = None
    next_steps: Annotated[
        str | None,
        Field(alias='nextSteps', description='Description of the next steps'),
    ] = None


class TrackingShipmentEvent(TrackingShipmentStatus):
    piece_ids: Annotated[
        list[PieceId] | None,
        Field(
            alias='pieceIds',
            description='Ids of all the items or pieces in the shipment',
        ),
    ] = None


class ValueAddedServices(DhlModel):
    services: Annotated[
        list[ValueAddedService] | None, Field(description='List of customer services')
    ] = None


class TrackingShipmentDetails(DhlModel):
    product: Product | None = None
    provider: Provider | None = None
    receiver: PersonEntity | None = None
    sender: PersonEntity | None = None
    carrier: PersonEntity | None = None
    shipper: PersonEntity | None = None
    consignee: PersonEntity | None = None
    proof_of_delivery: Annotated[
        ProofOfDelivery | None, Field(alias='proofOfDelivery')
    ] = None
    proof_of_delivery_signed_available: Annotated[
        bool | None,
        Field(
            alias='proofOfDeliverySignedAvailable',
            description="\\'Yes\\' if signer identification is available",
        ),
    ] = None
    total_number_of_pieces: Annotated[
        int | None,
        Field(
            alias='totalNumberOfPieces',
            description='Total number of items or pieces in the shipment',
        ),
    ] = None
    piece_ids: Annotated[
        list[PieceId] | None,
        Field(
            alias='pieceIds',
            description='Ids of all the items or pieces in the shipment',
        ),
    ] = None
    weight: QuantitativeValue | None = None
    volume: QuantitativeValue | None = None
    loading_meters: Annotated[
        float | None,
        Field(
            alias='loadingMeters',
            description='A loading meter standard unit of measurement for transport by truck',
        ),
    ] = None
    dimensions: Dimensions | None = None
    references: Annotated[
        list[Reference] | None,
        Field(description='A list of indications that refers to related shipment'),
    ] = None
    value_added_services: Annotated[
        ValueAddedServices | None, Field(alias='valueAddedServices')
    ] = None
    controlled_data_codes: Annotated[
        list[ControlledDataCode] | None,
        Field(
            alias='controlledDataCodes',
            description='Extra Controlled Access Data Codes',
        ),
    ] = None
    shipment_activation_date: Annotated[
        str | None,
        Field(alias='shipmentActivationDate', description='Shipment Activation date'),
    ] = None
    dgf_routes: Annotated[
        list[DgfRoute] | None,
        Field(alias='dgf:routes', description='DHL Global Forwarding routing Details'),
    ] = None
    telemetry: Annotated[
        list[Measurement] | None,
        Field(description='list of all sensor measurements from devices'),
    ] = None


class TrackingShipment(DhlModel):
    field_ttl: Annotated[Ttl | None, Field(alias='@ttl', validate_default=True)] = (
        15552000
    )
    id: Annotated[
        str | None, Field(description='Shipment identification tracking number')
    ] = None
    service: Service | None = None
    division: Annotated[
        str | None,
        Field(
            description='The (sub)division of service provider that owns the shipment'
        ),
    ] = None
    origin: SecuredPlace | None = None
    destination: SecuredPlace | None = None
    status: TrackingShipmentStatus | None = None
    pick_up_date: Annotated[
        str | None, Field(alias='pickUpDate', description='Shipment pickup date')
    ] = None
    estimated_time_of_delivery: Annotated[
        str | None,
        Field(
            alias='estimatedTimeOfDelivery', description='Estimated time of delivery'
        ),
    ] = None
    estimated_delivery_time_frame: Annotated[
        EstimatedDeliveryTimeFrame | None, Field(alias='estimatedDeliveryTimeFrame')
    ] = None
    estimated_time_of_delivery_remark: Annotated[
        str | None,
        Field(
            alias='estimatedTimeOfDeliveryRemark',
            description='Human-readable description of the estimated delivery time',
        ),
    ] = None
    service_url: Annotated[
        AnyUrl | None,
        Field(alias='serviceUrl', description='Custom link to BU tracking service'),
    ] = None
    reroute_url: Annotated[
        AnyUrl | None,
        Field(
            alias='rerouteUrl',
            description='Custom link to BU rerouting service, if available for the current status of the shipment',
        ),
    ] = None
    return_flag: Annotated[
        ReturnFlag | None, Field(alias='returnFlag', validate_default=True)
    ] = False
    details: TrackingShipmentDetails | None = None
    events: Annotated[
        list[TrackingShipmentEvent] | None,
        Field(description='Historical list of events & timestamps'),
    ] = None


class TrackingShipments(DhlModel):
    url: Annotated[AnyUrl | None, Field(description='A link to current page')] = None
    prev_url: Annotated[
        AnyUrl | None, Field(alias='prevUrl', description='A link to the previous page')
    ] = None
    next_url: Annotated[
        AnyUrl | None, Field(alias='nextUrl', description='A link to the next page')
    ] = None
    first_url: Annotated[
        AnyUrl | None, Field(alias='firstUrl', description='A link to the first page')
    ] = None
    last_url: Annotated[
        AnyUrl | None, Field(alias='lastUrl', description='A link to the last page')
    ] = None
    shipments: Annotated[
        list[TrackingShipment] | None,
        Field(description='An array of unified tracking shipments'),
    ] = None
    possible_additional_shipments_url: Annotated[
        list[AnyUrl] | None,
        Field(
            alias='possibleAdditionalShipmentsUrl',
            description='An array of business services, where should be potentially shipment found',
        ),
    ] = None

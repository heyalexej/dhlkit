# Generated from an official DHL OpenAPI document. DO NOT EDIT.

from __future__ import annotations

from typing import Annotated, Literal

from dhlkit.models import DhlModel
from pydantic import Field, RootModel


class EmailNotification(DhlModel):
    send_pickup_confirmation_email: Annotated[
        bool | None, Field(alias='sendPickupConfirmationEmail')
    ] = None
    send_pickup_time_window_email: Annotated[
        bool | None, Field(alias='sendPickupTimeWindowEmail')
    ] = None


class PickupASAP(DhlModel):
    type: Literal['ASAP']


class TimeFrame(DhlModel):
    time_from: Annotated[
        str | None, Field(alias='timeFrom', pattern='^\\d{2}:\\d{2}$')
    ] = None
    time_until: Annotated[
        str | None, Field(alias='timeUntil', pattern='^\\d{2}:\\d{2}$')
    ] = None


class BulkService(DhlModel):
    comment: Annotated[str, Field(max_length=50)]


class TransportationType(
    RootModel[
        Literal['PAKET', 'ROLLBEHAELTER', 'WECHSELBEHAELTER', 'PALETTEN', 'SPERRGUT']
    ]
):
    root: Annotated[
        Literal['PAKET', 'ROLLBEHAELTER', 'WECHSELBEHAELTER', 'PALETTEN', 'SPERRGUT'],
        Field(description='TBD documentation'),
    ]


class Weight(DhlModel):
    uom: Annotated[Literal['g', 'kg'], Field(description='metric unit for weight')] = (
        'g'
    )
    value: float


class Name(RootModel[str]):
    root: Annotated[str, Field(max_length=50)]


class AddressStreet(RootModel[str]):
    root: Annotated[str, Field(max_length=70)]


class AddressHouse(RootModel[str]):
    root: Annotated[str, Field(max_length=10)]


class PostalCode(RootModel[str]):
    root: Annotated[str, Field(max_length=7)]


class City(RootModel[str]):
    root: Annotated[str, Field(max_length=35)]


class Country(RootModel[str]):
    root: Annotated[str, Field(max_length=2, min_length=2)]


class State(RootModel[str]):
    root: Annotated[str, Field(max_length=35)]


class OrderID(RootModel[str]):
    root: Annotated[str, Field(max_length=32, min_length=32)]


class AsId(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description='The pickup location id',
            examples=['AS3254120698'],
            max_length=12,
            min_length=12,
            pattern='^AS[0-9]{10}$',
        ),
    ]


class AccountNumber(RootModel[str]):
    root: Annotated[str, Field(pattern='\\d{10}')]


class BillingNumber(RootModel[str]):
    root: Annotated[str, Field(pattern='\\d{10}\\d{2}\\w{2}')]


class SimpleDate(RootModel[str]):
    root: Annotated[str, Field(pattern='^\\d{4}-\\d{2}-\\d{2}$')]


class SimpleDateTime(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description='The date time (Central European Time [CET])',
            pattern='^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$',
        ),
    ]


class Error(DhlModel):
    error_code: Annotated[
        int, Field(alias='errorCode', description='The business-level error code.')
    ]
    title: Annotated[
        str, Field(description='A short, human-readable summary of the problem type.')
    ]
    instance: Annotated[
        str | None,
        Field(
            description='A URI reference that identifies the specific occurrence of the problem.'
        ),
    ] = None
    detail: Annotated[
        str | None,
        Field(
            description='A human-readable explanation specific to this occurrence of the problem.'
        ),
    ] = None


class CustomerDetails(DhlModel):
    account_number: Annotated[AccountNumber | None, Field(alias='accountNumber')] = None
    billing_number: Annotated[BillingNumber, Field(alias='billingNumber')]


class ContactPerson(DhlModel):
    name: Annotated[str | None, Field(max_length=50)] = None
    phone: Annotated[str | None, Field(max_length=50)] = None
    email: Annotated[str | None, Field(max_length=250)] = None
    email_notification: Annotated[
        EmailNotification | None, Field(alias='emailNotification')
    ] = None


class FixedDate(DhlModel):
    value: SimpleDate
    type: Literal['Date']


class OrderDetails(DhlModel):
    order_id: Annotated[OrderID, Field(alias='orderID')]
    order_state: Annotated[
        str,
        Field(
            alias='orderState',
            description='Mögliche Rückgabewerte: ANGENOMMEN, STORNIERT, ABGELEHNT, ABGEHOLT, TEILABHOLUNG, NICHT_ABGEHOLT, IN_DURCHFUEHRUNG, IN_PRUEFUNG, FREIGABE, TEILBESTAETIGT',
        ),
    ]


class ShipmentState(DhlModel):
    state: str
    response_time: Annotated[SimpleDateTime | None, Field(alias='responseTime')] = None
    actual_pickup_date: Annotated[
        SimpleDate | None, Field(alias='actualPickupDate')
    ] = None


class PickupLocationIdType(DhlModel):
    type: Literal['Id']
    as_id: Annotated[AsId, Field(alias='asId')]


class PickupAddress(DhlModel):
    name1: Name
    name2: Name | None = None
    address_street: Annotated[AddressStreet, Field(alias='addressStreet')]
    address_house: Annotated[AddressHouse, Field(alias='addressHouse')]
    postal_code: Annotated[PostalCode, Field(alias='postalCode')]
    city: City
    country: Country | None = None
    state: State | None = None


class ConsigneeAddress(DhlModel):
    name1: Name
    name2: Name | None = None
    address_street: Annotated[AddressStreet | None, Field(alias='addressStreet')] = None
    address_house: Annotated[AddressHouse | None, Field(alias='addressHouse')] = None
    postal_code: Annotated[PostalCode, Field(alias='postalCode')]
    city: City
    country: Country | None = None
    state: State | None = None


class ConfirmedShipment(DhlModel):
    transportation_type: Annotated[
        TransportationType, Field(alias='transportationType')
    ]
    shipment_no: Annotated[str | None, Field(alias='shipmentNo')] = None
    order_date: Annotated[SimpleDateTime, Field(alias='orderDate')]


class ValidationConfirmation(DhlModel):
    pickup_date: Annotated[SimpleDate, Field(alias='pickupDate')]
    free_of_charge: Annotated[bool, Field(alias='freeOfCharge')]
    pickup_type: Annotated[Literal['BDA', 'EZA', 'EMA'], Field(alias='pickupType')]


class ValideOrderResponse(DhlModel):
    value: ValidationConfirmation
    type: Literal['VALIDATION']


class ConfirmedCancellation(DhlModel):
    order_id: Annotated[OrderID, Field(alias='orderID')]
    order_state: Annotated[str, Field(alias='orderState')]
    message: str


class FailedCancellation(DhlModel):
    order_id: Annotated[OrderID, Field(alias='orderID')]
    order_state: Annotated[str | None, Field(alias='orderState')] = None
    message: str


class PickupLocationId(DhlModel):
    id: AsId | None = None
    pickup_address: Annotated[PickupAddress | None, Field(alias='pickupAddress')] = None


class PickupDetails(DhlModel):
    pickup_date: Annotated[
        FixedDate | PickupASAP, Field(alias='pickupDate', discriminator='type')
    ]
    total_weight: Annotated[Weight | None, Field(alias='totalWeight')] = None
    comment: Annotated[str | None, Field(max_length=100)] = None


class LabelService(DhlModel):
    consignee: ConsigneeAddress


class PickupAddressType(DhlModel):
    type: Literal['Address']
    pickup_address: Annotated[PickupAddress, Field(alias='pickupAddress')]


class PickupConfirmation(DhlModel):
    order_id: Annotated[OrderID, Field(alias='orderID')]
    pickup_date: Annotated[SimpleDate, Field(alias='pickupDate')]
    free_of_charge: Annotated[bool, Field(alias='freeOfCharge')]
    pickup_type: Annotated[
        Literal['BDA', 'EZA', 'EMA'], Field(alias='pickupType', description='TBD')
    ]
    confirmed_shipments: Annotated[
        list[ConfirmedShipment], Field(alias='confirmedShipments')
    ]


class CancelResult(DhlModel):
    confirmed_cancellations: Annotated[
        list[ConfirmedCancellation] | None, Field(alias='confirmedCancellations')
    ] = None
    failed_cancellations: Annotated[
        list[FailedCancellation] | None, Field(alias='failedCancellations')
    ] = None


class OrderPickupResponse(DhlModel):
    value: PickupConfirmation
    type: Literal['ORDERPICKUP']


class PickupServices(DhlModel):
    bulky_good: Annotated[BulkService | None, Field(alias='bulkyGood')] = None
    print_label: Annotated[LabelService | None, Field(alias='printLabel')] = None


class OrderResponse(DhlModel):
    confirmation: Annotated[
        OrderPickupResponse | ValideOrderResponse | None, Field(discriminator='type')
    ] = None


class Shipment(DhlModel):
    transportation_type: Annotated[
        TransportationType, Field(alias='transportationType')
    ]
    replacement: bool | None = None
    shipment_no: Annotated[str | None, Field(alias='shipmentNo')] = None
    size: Annotated[
        Literal['S', 'M', 'L'] | None,
        Field(description='mandatory if customerDetails.billingNumber is not set'),
    ] = None
    pickup_services: Annotated[PickupServices | None, Field(alias='pickupServices')] = (
        None
    )
    customer_reference: Annotated[
        str | None, Field(alias='customerReference', max_length=20)
    ] = None


class ShipmentDetails(DhlModel):
    shipments: Annotated[list[Shipment] | None, Field(min_length=1)] = None


class ShipmentWithState(DhlModel):
    shipment: Shipment
    shipment_state: Annotated[ShipmentState | None, Field(alias='shipmentState')] = None
    order_date: Annotated[SimpleDateTime, Field(alias='orderDate')]


class PickupOrder(DhlModel):
    customer_details: Annotated[
        CustomerDetails | None, Field(alias='customerDetails')
    ] = None
    pickup_location: Annotated[
        PickupLocationIdType | PickupAddressType,
        Field(alias='pickupLocation', discriminator='type'),
    ]
    business_hours: Annotated[
        list[TimeFrame] | None, Field(alias='businessHours', max_length=3, min_length=0)
    ] = None
    contact_person: Annotated[
        list[ContactPerson] | None,
        Field(alias='contactPerson', max_length=2, min_length=0),
    ] = None
    pickup_details: Annotated[PickupDetails, Field(alias='pickupDetails')]
    shipment_details: Annotated[ShipmentDetails, Field(alias='shipmentDetails')]


class ShipmentDetailsWithState(DhlModel):
    shipments: Annotated[list[ShipmentWithState] | None, Field(min_length=1)] = None


class PickupOrderStatus(DhlModel):
    order_details: Annotated[OrderDetails, Field(alias='orderDetails')]
    customer_details: Annotated[CustomerDetails, Field(alias='customerDetails')]
    pickup_location: Annotated[PickupLocationId, Field(alias='pickupLocation')]
    business_hours: Annotated[
        list[TimeFrame] | None, Field(alias='businessHours', max_length=3, min_length=0)
    ] = None
    contact_person: Annotated[
        list[ContactPerson] | None,
        Field(alias='contactPerson', max_length=2, min_length=0),
    ] = None
    pickup_details: Annotated[PickupDetails, Field(alias='pickupDetails')]
    shipment_details: Annotated[
        ShipmentDetailsWithState, Field(alias='shipmentDetails')
    ]
    feedback: str | None = None

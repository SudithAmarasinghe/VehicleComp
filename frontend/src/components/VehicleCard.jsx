import React from 'react';
import { Car, MapPin, Calendar, Gauge } from 'lucide-react';
import './VehicleCard.css';

const VehicleCard = ({ vehicle }) => {
    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-LK', {
            style: 'currency',
            currency: 'LKR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(price);
    };

    return (
        <div className="vehicle-card">
            {vehicle.image_url && (
                <div className="vehicle-image">
                    <img src={vehicle.image_url} alt={vehicle.title} />
                </div>
            )}

            <div className="vehicle-content">
                <h3 className="vehicle-title">{vehicle.title}</h3>

                <div className="vehicle-price">
                    {formatPrice(vehicle.price)}
                </div>

                <div className="vehicle-details">
                    {vehicle.year && (
                        <div className="detail-item">
                            <Calendar size={16} />
                            <span>{vehicle.year}</span>
                        </div>
                    )}

                    {vehicle.mileage && vehicle.mileage !== 'N/A' && (
                        <div className="detail-item">
                            <Gauge size={16} />
                            <span>{vehicle.mileage}</span>
                        </div>
                    )}

                    {vehicle.location && vehicle.location !== 'N/A' && (
                        <div className="detail-item">
                            <MapPin size={16} />
                            <span>{vehicle.location}</span>
                        </div>
                    )}
                </div>

                <div className="vehicle-footer">
                    <span className="vehicle-source">{vehicle.source}</span>
                    {vehicle.url && (
                        <a
                            href={vehicle.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="view-listing-btn"
                        >
                            View Listing →
                        </a>
                    )}
                </div>
            </div>
        </div>
    );
};

export default VehicleCard;

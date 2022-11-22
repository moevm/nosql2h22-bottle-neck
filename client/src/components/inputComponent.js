import * as React from 'react';
export default function InputComponent({label , type, value, onChange, variant}) {
    if(variant === 'input'){
        return (
            <div >
                <label>
                    <input
                        type={type}
                        defaultValue={value}
                        onChange={onChange}
                    />

                    {label}
                </label>

            </div>
        )
    }
    return (
    <div>
        <label>
            {label}

        </label>
        <br/>
        <input
            type={type}
            defaultValue={value}
            onChange={onChange}
        />
    </div>
        )
}

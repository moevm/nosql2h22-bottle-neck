import * as React from 'react';
export default function InputComponent({label , type, value, onChange, variant, sRef, placeholder=null}) {
    if(variant === 'input'){
        return (
            <div >
                <label>
                    <input
                        ref={sRef}
                        type={type}
                        defaultValue={value}
                        placeholder={placeholder}
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
            ref={sRef}
            type={type}
            defaultValue={value}
            onChange={onChange}
        />
    </div>
        )
}

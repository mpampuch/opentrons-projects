from opentrons import protocol_api

metadata = {
    'protocolName': 'DNA Extraction Protocol',
    'author': 'Assistant',
    'description': 'DNA extraction protocol with manual intervention steps'
}

requirements = {
    "robotType": "OT-2",
    "apiLevel": "2.19"
}

def run(protocol: protocol_api.ProtocolContext):
    # Load modules
    temp_module = protocol.load_module('temperature module gen2', 1)
    # heater_shaker = protocol.load_module('heaterShakerModuleV1', 4)
    
    # Load labware
    source_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', 2)
    tiprack_1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', 3)
    reservoir = protocol.load_labware('nest_12_reservoir_15ml', 6)
    
    # Load pipettes
    p1000 = protocol.load_instrument('p1000_single_gen2', 'left', tip_racks=[tiprack_1000])

    # Protocol starts after manual sample preparation
    protocol.pause('''
    Please prepare samples:
    1. Process leaf tissue and add 40mg powder to tubes in position 2
    2. Place tubes in source rack
    3. Add reagents to reservoir:
       - A1: HMW Lysis Buffer A
       - A2: RNase A Solution
       - A3: Proteinase K Solution
       - A4: Protein Precipitation Solution
       - A5: 70% ethanol
       - A6: DNA Rehydration Solution
    4. Click RESUME when ready
    ''')

    # Add Lysis Buffer
    p1000.transfer(500, reservoir['A1'], source_rack.wells()[0], new_tip='once')
    
    # Set temperature for lysis
    temp_module.set_temperature(65)
    protocol.delay(minutes=15)
    protocol.pause("Remove tubes and vortex 1-5 seconds. Return tubes and click RESUME.")
    
    # Cool to room temp
    temp_module.set_temperature(25)
    protocol.delay(minutes=5)
    
    # Add RNase A
    p1000.transfer(3, reservoir['A2'], source_rack.wells()[0], new_tip='always')
    
    # Set temperature for RNase treatment
    temp_module.set_temperature(37)
    protocol.delay(minutes=15)
    
    # Add Proteinase K
    p1000.transfer(20, reservoir['A3'], source_rack.wells()[0], new_tip='always')
    
    # Set temperature for Proteinase K treatment
    temp_module.set_temperature(56)
    protocol.delay(minutes=15)
    
    protocol.pause('''
    Please perform manual steps:
    1. Remove tubes and centrifuge at 13,000-16,000 × g for 3 minutes
    2. Transfer lysate to clean tubes
    3. Place tubes back in source rack
    4. Click RESUME when ready
    ''')
    
    # Add Protein Precipitation Solution
    p1000.transfer(200, reservoir['A4'], source_rack.wells()[0], new_tip='always')
    
    protocol.pause('''
    Please perform manual steps:
    1. Remove tubes for centrifugation and protein precipitation
    2. Place new tubes in rack
    3. Click RESUME when ready for next liquid handling step
    ''')
    
    # Add ethanol wash
    p1000.transfer(600, reservoir['A5'], source_rack.wells()[0], new_tip='always')
    
    protocol.pause('''
    Please perform manual steps:
    1. Remove tubes for centrifugation
    2. Discard supernatant
    3. Return tubes to rack
    4. Click RESUME for second ethanol wash
    ''')
    
    # Second ethanol wash
    p1000.transfer(600, reservoir['A5'], source_rack.wells()[0], new_tip='always')
    
    protocol.pause('''
    Please perform manual steps:
    1. Remove tubes for centrifugation
    2. Discard supernatant
    3. Air-dry pellet for 10-15 minutes
    4. Return tubes to rack
    5. Click RESUME when ready for rehydration
    ''')
    
    # Add DNA Rehydration Solution
    p1000.transfer(100, reservoir['A6'], source_rack.wells()[0], new_tip='always')
    
    # Final incubation
    temp_module.set_temperature(65)
    protocol.delay(minutes=60)
    
    # Deactivate temperature module
    temp_module.deactivate()
    
    protocol.comment("Protocol complete. Store DNA at 2-8°C.")